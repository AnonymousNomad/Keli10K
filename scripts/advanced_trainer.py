import sys
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import math
import time
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

device = 'cuda' if torch.cuda.is_available() else 'cpu'
PAD = 0


class SwarmDataset(Dataset):
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
        mask = [0]*len(item.get('input_ids', [])) + [1]*len(item.get('target_ids', []))
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


class AdvancedTrainer:
    def __init__(self, model_cfg, tokenizer, lr=5e-4, batch_size=16, accum_steps=2, checkpoint_dir='checkpoints'):
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        self.accum_steps = accum_steps
        self.model_cfg = model_cfg
        self.checkpoint_dir = checkpoint_dir
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

        self._create_model()
        self.optimizer = torch.optim.AdamW(
            self.model.model.parameters(), lr=lr, weight_decay=0.01, betas=(0.9, 0.95)
        )

        self.history = {
            'train_loss': [], 'train_acc': [],
            'val_loss': [], 'val_acc': [], 'val_ppl': [],
            'domain_acc': {},
            'steps': [], 'lr': [], 'phase': [],
        }
        self.best_val_acc = 0.0
        self.best_val_loss = float('inf')
        self.no_improve_count = 0
        self.current_step = 0

    def _create_model(self):
        from keli_10k import Keli10KModel
        self.model = Keli10KModel(self.model_cfg)

    def train(self, train_data, val_data, epochs=5, start_step=0, phase_name="default"):
        train_dataset = SwarmDataset(train_data)
        train_loader = DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True, collate_fn=collate_batch,
        )
        val_dataset = SwarmDataset(val_data) if val_data else None
        val_loader = DataLoader(
            val_dataset, batch_size=self.batch_size, shuffle=False, collate_fn=collate_batch,
        ) if val_dataset else None

        total_steps = epochs * len(train_loader) // self.accum_steps
        warmup_steps = min(500, total_steps // 10)
        global_step = start_step

        def get_lr(step):
            if step < warmup_steps:
                return 5e-4 * (step + 1) / (warmup_steps + 1)
            progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
            return 5e-4 * 0.5 * (1.0 + math.cos(math.pi * progress))

        print(f"\n  Phase '{phase_name}': {len(train_data)} train / {len(val_data)} val")
        print(f"  Epochs: {epochs}, total steps: ~{total_steps}, warmup: {warmup_steps}")

        for epoch in range(epochs):
            self.model.model.train()
            epoch_start = time.time()
            epoch_loss = 0.0
            epoch_acc = 0.0
            n_batches = 0
            accum_loss = 0.0
            accum_acc = 0.0
            accum_count = 0

            for batch_idx, (input_ids, mask, modes, domains) in enumerate(train_loader):
                lr = get_lr(global_step)
                for pg in self.optimizer.param_groups:
                    pg['lr'] = lr

                input_ids = input_ids.to(device)
                mask = mask.to(device)
                targets = input_ids.clone()
                targets[targets == PAD] = -100

                is_build = all(m == 'build' for m in modes)
                logits, _ = self.model.model(input_ids, mode='build' if is_build else 'plan')
                loss, acc = compute_loss_and_acc(logits, targets, mask)

                loss = loss / self.accum_steps
                loss.backward()

                accum_loss += loss.item()
                accum_acc += acc.item()
                accum_count += 1

                if (batch_idx + 1) % self.accum_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.model.parameters(), 1.0)
                    self.optimizer.step()
                    self.optimizer.zero_grad()

                    step_loss = accum_loss / accum_count
                    step_acc = accum_acc / accum_count
                    epoch_loss += step_loss
                    epoch_acc += step_acc
                    n_batches += 1
                    global_step += 1
                    self.current_step = global_step

                    self.history['train_loss'].append(step_loss)
                    self.history['train_acc'].append(step_acc)
                    self.history['lr'].append(lr)
                    self.history['phase'].append(phase_name)

                    accum_loss = 0.0
                    accum_acc = 0.0
                    accum_count = 0

                    if global_step % 100 == 0:
                        ppl = math.exp(min(step_loss, 20))
                        print(f"    Step {global_step:5d} | loss={step_loss:.4f} acc={step_acc:.4f} ppl={ppl:.2f} lr={lr:.2e}")

                    if global_step > 0 and global_step % 500 == 0 and val_loader:
                        self._validate_and_log(val_loader, global_step, val_data)

            avg_loss = epoch_loss / max(n_batches, 1)
            avg_acc = epoch_acc / max(n_batches, 1)
            epoch_time = time.time() - epoch_start

            val_str = ""
            if val_loader:
                vl, va, vp = self._validate(val_loader)
                val_str = f" val_loss={vl:.4f} val_acc={va:.4f} val_ppl={vp:.2f}"

            print(f"  Epoch {epoch+1}/{epochs}: loss={avg_loss:.4f} acc={avg_acc:.4f}{val_str} ({epoch_time:.1f}s)")

        return global_step

    def _validate(self, loader):
        self.model.model.eval()
        total_loss = 0.0
        total_acc = 0.0
        n = 0
        with torch.no_grad():
            for input_ids, mask, modes, domains in loader:
                input_ids = input_ids.to(device)
                mask = mask.to(device)
                targets = input_ids.clone()
                targets[targets == PAD] = -100
                is_build = all(m == 'build' for m in modes)
                logits, _ = self.model.model(input_ids, mode='build' if is_build else 'plan')
                loss, acc = compute_loss_and_acc(logits, targets, mask)
                total_loss += loss.item()
                total_acc += acc.item()
                n += 1
        self.model.model.train()
        avg_loss = total_loss / max(n, 1)
        avg_acc = total_acc / max(n, 1)
        ppl = math.exp(min(avg_loss, 20))
        return avg_loss, avg_acc, ppl

    def _validate_and_log(self, loader, step, val_data):
        self.model.model.eval()
        total_loss = 0.0
        total_acc = 0.0
        domain_acc = defaultdict(list)
        n = 0

        val_dataset = loader.dataset
        with torch.no_grad():
            for input_ids, mask, modes, domains in loader:
                input_ids = input_ids.to(device)
                mask = mask.to(device)
                targets = input_ids.clone()
                targets[targets == PAD] = -100
                is_build = all(m == 'build' for m in modes)
                logits, _ = self.model.model(input_ids, mode='build' if is_build else 'plan')
                loss, acc = compute_loss_and_acc(logits, targets, mask)
                total_loss += loss.item()
                total_acc += acc.item()
                n += 1
                for d in domains:
                    domain_acc[d].append(acc.item())

        self.model.model.train()
        avg_loss = total_loss / max(n, 1)
        avg_acc = total_acc / max(n, 1)
        ppl = math.exp(min(avg_loss, 20))

        self.history['val_loss'].append(avg_loss)
        self.history['val_acc'].append(avg_acc)
        self.history['val_ppl'].append(ppl)
        self.history['steps'].append(step)

        domain_str = ""
        for d, accs in sorted(domain_acc.items()):
            d_acc = sum(accs) / len(accs)
            domain_str += f" {d}={d_acc:.4f}"

        acc_str = f"val_loss={avg_loss:.4f} val_acc={avg_acc:.4f} val_ppl={ppl:.2f}"
        if avg_acc > self.best_val_acc:
            self.best_val_acc = avg_acc
            self.best_val_loss = avg_loss
            self.no_improve_count = 0
            self.save_checkpoint(f'{self.checkpoint_dir}/keli_best.pt')
            print(f"    ** {acc_str}{domain_str} ** NEW BEST")
        else:
            self.no_improve_count += 1
            print(f"    {acc_str}{domain_str} (no improve {self.no_improve_count}/5)")
            if self.no_improve_count >= 5:
                print(f"    Early stopping at step {step}")
                return

    def save_checkpoint(self, path):
        if self.model:
            self.model.save(path)
            hist = {k: v for k, v in self.history.items()}
            hist['best_val_acc'] = self.best_val_acc
            hist['current_step'] = self.current_step
            hist_path = Path(path).with_suffix('.hist.json')
            with open(hist_path, 'w') as f:
                json.dump(hist, f, indent=2)
            print(f"    Checkpoint -> {path}")

    def load_checkpoint(self, path):
        self._create_model()
        self.model.load(path)
        hist_path = Path(path).with_suffix('.hist.json')
        if hist_path.exists():
            with open(hist_path) as f:
                self.history = json.load(f)
            self.best_val_acc = self.history.get('best_val_acc', 0.0)
            self.current_step = self.history.get('current_step', 0)
        print(f"  Loaded checkpoint from {path} (step {self.current_step})")


def load_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', default='frontend')
    parser.add_argument('--data', default='data/advanced/train.jsonl')
    parser.add_argument('--val', default='data/advanced/val.jsonl')
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--accum', type=int, default=2)
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--checkpoint-dir', default='checkpoints')
    parser.add_argument('--resume', default=None)
    args = parser.parse_args()

    from snca_config import SNCACfg
    from snca_tokenizer import SNCATokenizer
    cfg = SNCACfg()
    tok = SNCATokenizer()

    print(f"Loading data: {args.data}")
    train_data = load_jsonl(args.data)
    val_data = load_jsonl(args.val)

    if args.phase != 'mixed':
        train_data = [d for d in train_data if d.get('domain', '') == args.phase]
        val_data = [d for d in val_data if d.get('domain', '') == args.phase]

    print(f"  Train: {len(train_data)} | Val: {len(val_data)}")

    trainer = AdvancedTrainer(
        cfg, tok, lr=args.lr, batch_size=args.batch_size,
        accum_steps=args.accum, checkpoint_dir=args.checkpoint_dir,
    )

    if args.resume:
        trainer.load_checkpoint(args.resume)

    trainer.train(train_data, val_data, epochs=args.epochs, phase_name=args.phase)

    final_path = f'{args.checkpoint_dir}/keli_{args.phase}.pt'
    trainer.save_checkpoint(final_path)

    if trainer.history.get('val_acc'):
        best = max(trainer.history['val_acc'])
        print(f"\nPhase '{args.phase}' best val acc: {best:.4f} ({best*100:.1f}%)")


if __name__ == '__main__':
    main()
