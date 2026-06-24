import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
import math
import time
from pathlib import Path
from torch.utils.data import Dataset, DataLoader

device = 'cuda' if torch.cuda.is_available() else 'cpu'
PAD = 0


class SwarmDataset(Dataset):
    def __init__(self, data, max_len=1024):
        self.samples = []
        for item in data:
            input_ids = item.get('input_ids', [])
            target_ids = item.get('target_ids', [])
            mode = item.get('mode', 'plan')
            if not input_ids or not target_ids:
                continue
            if len(input_ids) > max_len:
                input_ids = input_ids[:max_len]
            if len(target_ids) > max_len:
                target_ids = target_ids[:max_len]
            mask = [0] * len(input_ids) + [1] * len(target_ids)
            combined = input_ids + target_ids
            if len(combined) > max_len:
                combined = combined[:max_len]
                mask = mask[:max_len]
            if len(combined) > 0:
                self.samples.append({'input_ids': combined, 'mask': mask, 'mode': mode})

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return {
            'input_ids': torch.tensor(s['input_ids'], dtype=torch.long),
            'mask': torch.tensor(s['mask'], dtype=torch.float),
            'mode': s['mode'],
        }


def collate_batch(batch):
    input_ids = [b['input_ids'] for b in batch]
    masks = [b['mask'] for b in batch]
    modes = [b['mode'] for b in batch]
    max_len = max(len(ids) for ids in input_ids)
    padded_ids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    padded_masks = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (ids, m) in enumerate(zip(input_ids, masks)):
        padded_ids[i, :len(ids)] = ids
        padded_masks[i, :len(m)] = torch.as_tensor(m, dtype=torch.float)
    return padded_ids, padded_masks, modes


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


class SwarmTrainer:
    def __init__(self, model_cfg, tokenizer, lr=5e-4, batch_size=16, accum_steps=2):
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        self.accum_steps = accum_steps
        self.model_cfg = model_cfg
        self.model = None
        self.history = {
            'train_loss': [], 'train_acc': [],
            'val_loss': [], 'val_acc': [], 'val_ppl': [],
            'steps': [], 'lr': [],
        }
        self.best_val_acc = 0.0
        self.no_improve_count = 0

    def _create_model(self):
        from keli_10k import Keli10KModel
        self.model = Keli10KModel(self.model_cfg)
        return self.model

    def train(self, train_data, val_data, epochs=15, start_step=0):
        if self.model is None:
            self._create_model()

        optimizer = torch.optim.AdamW(
            self.model.model.parameters(), lr=5e-4, weight_decay=0.01, betas=(0.9, 0.95)
        )

        train_dataset = SwarmDataset(train_data)
        train_loader = DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True,
            collate_fn=collate_batch,
        )
        val_dataset = SwarmDataset(val_data) if val_data else None
        val_loader = DataLoader(
            val_dataset, batch_size=self.batch_size, shuffle=False,
            collate_fn=collate_batch,
        ) if val_dataset else None

        total_steps = epochs * len(train_loader)
        warmup_steps = min(500, total_steps // 10)

        def get_lr(step):
            if step < warmup_steps:
                return 5e-4 * (step + 1) / (warmup_steps + 1)
            progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
            return 5e-4 * 0.5 * (1.0 + math.cos(math.pi * progress))

        global_step = start_step
        total_train_time = 0.0
        accum_loss = 0.0
        accum_acc = 0.0
        accum_count = 0
        effective_batch = self.batch_size * self.accum_steps

        print(f"Training {self.model.model.count_parameters()/1e6:.2f}M model on {device}")
        print(f"  Data: {len(train_data)} train / {len(val_data)} val")
        print(f"  Batch: {self.batch_size} (eff {effective_batch}), accum: {self.accum_steps}")
        print(f"  Epochs: {epochs}, total steps: {total_steps}, warmup: {warmup_steps}")
        print()

        for epoch in range(epochs):
            self.model.model.train()
            epoch_start = time.time()
            epoch_loss = 0.0
            epoch_acc = 0.0
            n_batches = 0

            for batch_idx, (input_ids, mask, modes) in enumerate(train_loader):
                lr = get_lr(global_step)
                for pg in optimizer.param_groups:
                    pg['lr'] = lr

                input_ids = input_ids.to(device)
                mask = mask.to(device)
                targets = input_ids.clone()
                targets[targets == PAD] = -100

                batch_modes = modes
                is_build = all(m == 'build' for m in batch_modes)
                logits, _ = self.model.model(input_ids, mode='build' if is_build else 'plan')

                loss, acc = compute_loss_and_acc(logits, targets, mask)
                loss = loss / self.accum_steps
                loss.backward()

                accum_loss += loss.item()
                accum_acc += acc.item()
                accum_count += 1

                if (batch_idx + 1) % self.accum_steps == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.model.parameters(), 1.0)
                    optimizer.step()
                    optimizer.zero_grad()

                    step_loss = accum_loss / accum_count
                    step_acc = accum_acc / accum_count
                    epoch_loss += step_loss
                    epoch_acc += step_acc
                    n_batches += 1
                    global_step += 1

                    self.history['train_loss'].append(step_loss)
                    self.history['train_acc'].append(step_acc)
                    self.history['lr'].append(lr)

                    accum_loss = 0.0
                    accum_acc = 0.0
                    accum_count = 0

                    if global_step % 50 == 0:
                        ppl = math.exp(min(step_loss, 20))
                        print(f"  Step {global_step:5d} | loss={step_loss:.4f} acc={step_acc:.4f} ppl={ppl:.2f} lr={lr:.2e}")

                    if global_step > 0 and global_step % 200 == 0 and val_loader:
                        val_loss, val_acc, val_ppl = self._validate(val_loader)
                        self.history['val_loss'].append(val_loss)
                        self.history['val_acc'].append(val_acc)
                        self.history['val_ppl'].append(val_ppl)
                        self.history['steps'].append(global_step)

                        acc_str = f"val_loss={val_loss:.4f} val_acc={val_acc:.4f} val_ppl={val_ppl:.2f}"
                        if val_acc > self.best_val_acc:
                            self.best_val_acc = val_acc
                            self.no_improve_count = 0
                            self.save_checkpoint('checkpoints/swarm_best.pt')
                            print(f"  ** {acc_str} ** NEW BEST (acc={val_acc:.4f})")
                        else:
                            self.no_improve_count += 1
                            print(f"  {acc_str} (no improve {self.no_improve_count}/5)")
                            if self.no_improve_count >= 5:
                                print(f"  Early stopping at step {global_step}")
                                print(f"  Best val accuracy: {self.best_val_acc:.4f}")
                                return global_step

                    if global_step > 0 and global_step % 1000 == 0:
                        self.save_checkpoint(f'checkpoints/swarm_step_{global_step}.pt')

            if n_batches > 0:
                avg_loss = epoch_loss / n_batches
                avg_acc = epoch_acc / n_batches
            else:
                avg_loss = epoch_loss
                avg_acc = epoch_acc
            epoch_time = time.time() - epoch_start

            val_str = ""
            if val_loader:
                vl, va, vp = self._validate(val_loader)
                val_str = f" val_loss={vl:.4f} val_acc={va:.4f} val_ppl={vp:.2f}"

            print(f"Epoch {epoch+1}/{epochs}: loss={avg_loss:.4f} acc={avg_acc:.4f}{val_str} ({epoch_time:.1f}s)")

        print(f"\nTraining complete: {global_step} steps in {total_train_time:.1f}s")
        print(f"Best val accuracy: {self.best_val_acc:.4f}")
        return global_step

    def _validate(self, loader):
        self.model.model.eval()
        total_loss = 0.0
        total_acc = 0.0
        n = 0
        with torch.no_grad():
            for input_ids, mask, modes in loader:
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

    def save_checkpoint(self, path):
        if self.model:
            self.model.save(path)
            hist = {k: v for k, v in self.history.items()}
            hist['best_val_acc'] = self.best_val_acc
            hist_path = Path(path).with_suffix('.hist.json')
            with open(hist_path, 'w') as f:
                json.dump(hist, f, indent=2)
            print(f"  Checkpoint -> {path}")

    def load_checkpoint(self, path):
        self._create_model()
        self.model.load(path)
        hist_path = Path(path).with_suffix('.hist.json')
        if hist_path.exists():
            with open(hist_path) as f:
                self.history = json.load(f)
            self.best_val_acc = self.history.get('best_val_acc', 0.0)
        print(f"  Loaded checkpoint from {path}")


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
    parser.add_argument('--mode', default='swarm', choices=['swarm'])
    parser.add_argument('--data', default='data/generated/train.jsonl')
    parser.add_argument('--val', default='data/generated/val.jsonl')
    parser.add_argument('--epochs', type=int, default=15)
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--accum', type=int, default=2, help='gradient accumulation steps')
    parser.add_argument('--lr', type=float, default=5e-4)
    parser.add_argument('--resume', default=None)
    args = parser.parse_args()

    from snca_config import SNCACfg
    from snca_tokenizer import SNCATokenizer
    cfg = SNCACfg()
    tok = SNCATokenizer()

    print(f"Loading data...")
    train_data = load_jsonl(args.data)
    val_data = load_jsonl(args.val)
    print(f"  Train: {len(train_data)} | Val: {len(val_data)}")

    trainer = SwarmTrainer(cfg, tok, lr=args.lr, batch_size=args.batch_size, accum_steps=args.accum)

    start_step = 0
    if args.resume:
        trainer.load_checkpoint(args.resume)
        start_step = trainer.history['steps'][-1] if trainer.history.get('steps') else 0
        print(f"  Resuming from step {start_step}")
    else:
        print("Building model...")
        sys.stdout.flush()
        trainer._create_model()
        sys.stdout.flush()

    print("Starting training...")
    sys.stdout.flush()
    trainer.train(train_data, val_data, epochs=args.epochs, start_step=start_step)
    trainer.save_checkpoint('checkpoints/swarm_final.pt')

    if trainer.history['val_acc']:
        best_acc = max(trainer.history['val_acc'])
        print(f"Best validation accuracy: {best_acc:.4f} ({best_acc*100:.1f}%)")
        if best_acc >= 0.90:
            print("TARGET REACHED: 90%+ validation accuracy")
        else:
            print(f"Target: 90%, current best: {best_acc*100:.1f}%")


if __name__ == '__main__':
    main()
