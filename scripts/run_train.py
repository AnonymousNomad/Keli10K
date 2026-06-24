import sys, os, json, math, time
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

torch.set_num_threads(2)
device = 'cpu'
PAD = 0


class LazyDataset(Dataset):
    def __init__(self, data, max_len=1024):
        self.data = data
        self.max_len = max_len
        self.valid_indices = [
            i for i, item in enumerate(data)
            if item.get('input_ids') and item.get('target_ids')
        ]

    def __len__(self):
        return len(self.valid_indices)

    def __getitem__(self, idx):
        item = self.data[self.valid_indices[idx]]
        ids = (item.get('input_ids', []) + item.get('target_ids', []))[:self.max_len]
        mask = [0] * len(item.get('input_ids', [])) + [1] * len(item.get('target_ids', []))
        mask = mask[:self.max_len]
        return {
            'input_ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.float),
            'mode': item.get('mode', 'plan'),
            'domain': item.get('domain', 'unknown'),
        }


def collate_batch(batch):
    input_ids = [b['input_ids'] for b in batch]
    masks = [b['mask'] for b in batch]
    modes = [b['mode'] for b in batch]
    domains = [b['domain'] for b in batch]
    max_len = max(len(ids) for ids in input_ids)
    padded_ids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    padded_masks = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (ids, m) in enumerate(zip(input_ids, masks)):
        padded_ids[i, :len(ids)] = ids
        padded_masks[i, :len(m)] = torch.as_tensor(m, dtype=torch.float)
    return padded_ids, padded_masks, modes, domains


def compute_loss_and_acc(logits, targets, mask):
    shift_logits = logits[:, :-1, :].contiguous()
    shift_targets = targets[:, 1:].contiguous()
    shift_mask = mask[:, 1:].contiguous()
    loss = F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_targets.view(-1),
        reduction='none',
    )
    loss = loss.view(shift_logits.size(0), -1)
    masked_loss = (loss * shift_mask).sum() / (shift_mask.sum() + 1e-8)
    preds = shift_logits.argmax(dim=-1)
    correct = (preds == shift_targets) * shift_mask.bool()
    acc = correct.sum().float() / (shift_mask.sum() + 1e-8)
    return masked_loss, acc


def load_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def main():
    from snca_config import SNCACfg
    from keli_10k import Keli10KModel

    cfg = SNCACfg()
    model = Keli10KModel(cfg)
    n_params = sum(p.numel() for p in model.model.parameters())
    print(f'Model: {n_params/1e6:.2f}M params')

    train_data = load_jsonl('data/combined/train.jsonl')
    val_data = load_jsonl('data/combined/val.jsonl')
    print(f'Train: {len(train_data)} | Val: {len(val_data)}')

    train_ds = LazyDataset(train_data)
    val_ds = LazyDataset(val_data)
    train_loader = DataLoader(train_ds, batch_size=4, shuffle=True, collate_fn=collate_batch)
    val_loader = DataLoader(val_ds, batch_size=4, shuffle=False, collate_fn=collate_batch)

    optimizer = torch.optim.AdamW(model.model.parameters(), lr=5e-4, weight_decay=0.01, betas=(0.9, 0.95))

    total_steps = 2 * len(train_loader) // 2
    warmup_steps = min(500, total_steps // 10)
    print(f'Total steps: ~{total_steps}, warmup: {warmup_steps}')

    def get_lr(step):
        if step < warmup_steps:
            return 5e-4 * (step + 1) / (warmup_steps + 1)
        progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
        return 5e-4 * 0.5 * (1.0 + math.cos(math.pi * progress))

    global_step = 0
    best_val_acc = 0.0
    no_improve_count = 0

    for epoch in range(2):
        model.model.train()
        accum_loss = 0.0
        accum_acc = 0.0
        accum_count = 0
        epoch_start = time.time()

        for batch_idx, (input_ids, mask, modes, domains) in enumerate(train_loader):
            lr = get_lr(global_step)
            for pg in optimizer.param_groups:
                pg['lr'] = lr

            targets = input_ids.clone()
            targets[targets == PAD] = -100

            is_build = all(m == 'build' for m in modes)
            logits, _ = model.model(input_ids, mode='build' if is_build else 'plan')
            loss, acc = compute_loss_and_acc(logits, targets, mask)

            loss = loss / 2
            loss.backward()

            accum_loss += loss.item()
            accum_acc += acc.item()
            accum_count += 1

            if (batch_idx + 1) % 2 == 0:
                torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()

                step_loss = accum_loss / accum_count
                step_acc = accum_acc / accum_count
                accum_loss = 0.0
                accum_acc = 0.0
                accum_count = 0
                global_step += 1

                if global_step % 100 == 0:
                    ppl = math.exp(min(step_loss, 20))
                    elapsed = time.time() - epoch_start
                    print(f'Step {global_step:5d} | loss={step_loss:.4f} acc={step_acc:.4f} ppl={ppl:.2f} lr={lr:.2e} ({elapsed:.1f}s)')
                    epoch_start = time.time()

                if global_step % 500 == 0:
                    model.model.eval()
                    val_loss = 0.0
                    val_acc = 0.0
                    n = 0
                    val_start = time.time()
                    print(f'  Validating ({len(val_loader)} batches)...')
                    with torch.no_grad():
                        for v_i, (v_ids, v_mask, v_modes, v_domains) in enumerate(val_loader):
                            v_targets = v_ids.clone()
                            v_targets[v_targets == PAD] = -100
                            v_is_build = all(m == 'build' for m in v_modes)
                            v_logits, _ = model.model(v_ids, mode='build' if v_is_build else 'plan')
                            v_l, v_a = compute_loss_and_acc(v_logits, v_targets, v_mask)
                            val_loss += v_l.item()
                            val_acc += v_a.item()
                            n += 1
                            if v_i % 500 == 0 and v_i > 0:
                                print(f'    val batch {v_i}/{len(val_loader)} ({time.time()-val_start:.0f}s)')
                    model.model.train()
                    avg_val_loss = val_loss / max(n, 1)
                    avg_val_acc = val_acc / max(n, 1)
                    val_ppl = math.exp(min(avg_val_loss, 20))
                    acc_str = f'val_loss={avg_val_loss:.4f} val_acc={avg_val_acc:.4f} val_ppl={val_ppl:.2f}'
                    if avg_val_acc > best_val_acc:
                        best_val_acc = avg_val_acc
                        no_improve_count = 0
                        torch.save({
                            'model_state': model.model.state_dict(),
                            'optimizer_state': optimizer.state_dict(),
                        }, 'checkpoints/keli_best.pt')
                        print(f'  ** {acc_str} ** NEW BEST')
                    else:
                        no_improve_count += 1
                        print(f'  {acc_str} (no improve {no_improve_count}/5)')
                        if no_improve_count >= 5:
                            print(f'Early stopping at step {global_step}')
                            torch.save({
                                'model_state': model.model.state_dict(),
                                'optimizer_state': optimizer.state_dict(),
                            }, 'checkpoints/keli_final.pt')
                            return

    torch.save({
        'model_state': model.model.state_dict(),
        'optimizer_state': optimizer.state_dict(),
    }, 'checkpoints/keli_final.pt')
    print(f'Training complete. Best val acc: {best_val_acc:.4f}')


if __name__ == '__main__':
    main()
