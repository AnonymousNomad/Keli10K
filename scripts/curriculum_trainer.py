#!/usr/bin/env python3
"""Curriculum trainer with regularization, checkpointing, monitoring."""
import sys, os, json, math, time, csv, random
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAD = 0
BOS = 2
LR_BASE = 1e-4
LR_MIN = 1e-6
WARMUP = 1000
BATCH_SIZE = 4
ACCUM = 2
VAL_EVERY = 250
PATIENCE = 4
MAX_EPOCHS = 7

CHECKPOINT_DIR = Path('checkpoints')
LOG_DIR = Path('logs')
CHECKPOINT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

TIER_PATHS = {
    'easy': 'data/combined/tiers/easy.jsonl',
    'medium': 'data/combined/tiers/medium.jsonl',
    'hard': 'data/combined/tiers/hard.jsonl',
}
TIER_SIZES = {'easy': 42059, 'medium': 42059, 'hard': 42059}


# ─── In-Memory Tier Dataset ──────────────────────────────────────────────

class TierDataset(Dataset):
    def __init__(self, tier, max_len=1024, augment=False):
        path = TIER_PATHS[tier]
        self.max_len = max_len
        self.augment = augment
        self.items = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if item.get('input_ids') and item.get('target_ids'):
                    self.items.append(item)
        print(f'  Loaded {len(self.items)} items from {tier}')

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        ids = (item['input_ids'] + item['target_ids'])[:self.max_len]
        mask = [0]*len(item['input_ids']) + [1]*len(item['target_ids'])
        mask = mask[:self.max_len]

        if self.augment and random.random() < 0.3:
            target_start = len([m for m in mask if m == 0])
            for i in range(target_start, len(ids)):
                if random.random() < 0.1:
                    ids[i] = BOS

        return {
            'input_ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.float),
            'mode': item.get('mode', 'plan'),
            'domain': item.get('domain', 'unknown'),
        }


def collate_fn(batch):
    input_ids = [b['input_ids'] for b in batch]
    masks = [b['mask'] for b in batch]
    modes = [b['mode'] for b in batch]
    domains = [b['domain'] for b in batch]
    max_len = max(len(ids) for ids in input_ids)
    pids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    pms = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (ids, m) in enumerate(zip(input_ids, masks)):
        pids[i, :len(ids)] = ids
        pms[i, :len(m)] = torch.as_tensor(m, dtype=torch.float)
    return pids, pms, modes, domains


# ─── Loss ─────────────────────────────────────────────────────────────────

def compute_loss(logits, targets, mask, smoothing=0.1):
    sl = logits[:, :-1, :].contiguous()
    st = targets[:, 1:].contiguous()
    sm = mask[:, 1:].contiguous()
    V = logits.size(-1)

    valid = (st != -100)
    st_safe = st.clamp(min=0)
    sm = sm * valid.float()

    if smoothing > 0:
        smooth_loss = -F.log_softmax(sl, dim=-1)
        smooth_targets = torch.full_like(smooth_loss, smoothing/(V-1))
        smooth_targets.scatter_(-1, st_safe.unsqueeze(-1), 1 - smoothing)
        loss = (smooth_loss * smooth_targets).sum(-1)
    else:
        loss = F.cross_entropy(sl.view(-1, V), st_safe.view(-1), reduction='none')
        loss = loss.view(sl.size(0), -1)

    masked_loss = (loss * sm).sum() / (sm.sum() + 1e-8)
    preds = sl.argmax(dim=-1)
    correct = ((preds == st_safe) * sm.bool()).sum().float()
    acc = correct / (sm.sum() + 1e-8)
    return masked_loss, acc


# ─── LR Scheduler ─────────────────────────────────────────────────────────

class LRScheduler:
    def __init__(self, optimizer, warmup=WARMUP, base_lr=LR_BASE, min_lr=LR_MIN):
        self.opt = optimizer
        self.warmup = warmup
        self.base_lr = base_lr
        self.min_lr = min_lr
        self.step_count = 0
        self.total_steps = None

    def set_total_steps(self, n):
        self.total_steps = n

    def step(self, val_loss=None):
        self.step_count += 1
        s = self.step_count
        if s < self.warmup:
            lr = self.base_lr * (s + 1) / (self.warmup + 1)
        elif self.total_steps:
            progress = (s - self.warmup) / max(self.total_steps - self.warmup, 1)
            lr = self.min_lr + 0.5*(self.base_lr-self.min_lr)*(1+math.cos(math.pi*progress))
        else:
            lr = self.base_lr
        if val_loss is not None:
            if not hasattr(self, '_best_loss'):
                self._best_loss = val_loss
                self._plateau = 0
            elif val_loss > self._best_loss * 0.99:
                self._plateau += 1
                if self._plateau >= 3:
                    lr *= 0.5
                    print(f'    LR reduced to {lr:.2e}')
                    self._plateau = 0
            else:
                self._best_loss = min(self._best_loss, val_loss)
                self._plateau = 0
        for pg in self.opt.param_groups:
            pg['lr'] = lr
        return lr


# ─── Checkpoint Manager ──────────────────────────────────────────────────

class CheckpointManager:
    def __init__(self, directory=CHECKPOINT_DIR):
        self.dir = directory

    def save(self, model, optimizer, step, val_acc, val_loss, tag='keli_best'):
        path = self.dir / f'{tag}.pt'
        torch.save({
            'model_state': model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'step': step, 'val_acc': val_acc, 'val_loss': val_loss,
        }, path)
        return path

    def load_best(self, model, optimizer=None):
        path = self.dir / 'keli_best.pt'
        best_v = sorted(self.dir.glob('keli_best_v*.pt'), key=lambda p: p.stat().st_mtime)
        ckpt_path = best_v[-1] if best_v else (path if path.exists() else None)
        if ckpt_path is None:
            return None
        print(f'Resuming from {ckpt_path}')
        ckpt = torch.load(ckpt_path, map_location='cpu')
        model.load(ckpt_path)
        if optimizer and 'optimizer_state' in ckpt:
            try:
                optimizer.load_state_dict(ckpt['optimizer_state'])
            except Exception:
                pass
        return ckpt.get('step', 0), ckpt.get('val_acc', 0.0)


def plot_training(csv_path='logs/training_log.csv', output_path='logs/training_curves.png'):
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return
    steps, tl, ta, vl, va = [], [], [], [], []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            if row.get('val_loss') and row['val_loss']:
                steps.append(int(row['step']))
                tl.append(float(row['train_loss']))
                ta.append(float(row['train_acc']))
                vl.append(float(row['val_loss']))
                va.append(float(row['val_acc']))
    if not steps:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(steps, tl, 'b-', label='Train Loss')
    axes[0].plot(steps, vl, 'r-', label='Val Loss')
    axes[0].set_xlabel('Step'); axes[0].set_ylabel('Loss')
    axes[0].legend(); axes[0].grid(True, alpha=0.3)
    axes[1].plot(steps, ta, 'b-', label='Train Acc')
    axes[1].plot(steps, va, 'r-', label='Val Acc')
    axes[1].set_xlabel('Step'); axes[1].set_ylabel('Accuracy')
    axes[1].legend(); axes[1].grid(True, alpha=0.3)
    plt.tight_layout(); plt.savefig(output_path, dpi=150); plt.close()
    print(f'  Plot saved: {output_path}')


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    from snca_config import SNCACfg
    from keli_10k import Keli10KModel

    cfg = SNCACfg()
    model = Keli10KModel(cfg)
    n_params = sum(p.numel() for p in model.model.parameters())
    print(f'Model: {n_params/1e6:.2f}M params, dropout={cfg.dropout}')

    optimizer = torch.optim.AdamW(model.model.parameters(), lr=LR_BASE, weight_decay=0.01, betas=(0.9,0.95))
    lr_sched = LRScheduler(optimizer)

    start_step = 0
    best_val_acc = 0.0

    CURRICULUM = {1:'easy',2:'easy',3:'medium',4:'medium',5:'hard',6:'hard',7:'hard'}
    global_step = start_step
    no_improve = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        tier = CURRICULUM[epoch]
        tier_size = TIER_SIZES[tier]
        steps_per_epoch = tier_size // BATCH_SIZE // ACCUM
        lr_sched.set_total_steps(steps_per_epoch * (MAX_EPOCHS - epoch + 1))
        print(f'\nEpoch {epoch}/{MAX_EPOCHS} - Tier: {tier} ({tier_size} docs, ~{steps_per_epoch} steps)')

        dataset = TierDataset(tier, max_len=1024, augment=(epoch >= 3))
        loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn, drop_last=True)

        model.model.train()
        accum_loss, accum_acc, accum_count = 0.0, 0.0, 0
        epoch_start = time.time()

        for batch_idx, (input_ids, mask, modes, domains) in enumerate(loader):
            lr = lr_sched.step()
            targets = input_ids.clone()
            targets[targets == PAD] = -100

            is_build = all(m == 'build' for m in modes)
            logits, _ = model.model(input_ids, mode='build' if is_build else 'plan')
            loss, acc = compute_loss(logits, targets, mask, smoothing=0.1)
            (loss / ACCUM).backward()

            accum_loss += loss.item()
            accum_acc += acc.item()
            accum_count += 1

            if (batch_idx + 1) % ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()

                step_loss = accum_loss / accum_count
                step_acc = accum_acc / accum_count
                accum_loss, accum_acc, accum_count = 0.0, 0.0, 0
                global_step += 1

                if global_step % 100 == 0:
                    ppl = math.exp(min(step_loss, 20))
                    elapsed = time.time() - epoch_start
                    print(f'  Step {global_step:5d} | loss={step_loss:.4f} acc={step_acc:.4f} ppl={ppl:.2f} lr={lr:.2e} epoch={epoch} ({elapsed:.1f}s)')
                    epoch_start = time.time()

                if global_step % VAL_EVERY == 0:
                    val_result = validate(model, global_step, epoch)
                    if val_result:
                        val_loss, val_acc, val_ppl = val_result
                        print(f'  >> val_loss={val_loss:.4f} val_acc={val_acc:.4f} val_ppl={val_ppl:.2f}')
                        if val_acc > best_val_acc:
                            best_val_acc = val_acc
                            no_improve = 0
                            ckpt_mgr.save(model.model, optimizer, global_step, val_acc, val_loss, f'keli_best_v{epoch}')
                            ckpt_mgr.save(model.model, optimizer, global_step, val_acc, val_loss, 'keli_best')
                            print(f'    ** NEW BEST: {val_acc:.4f} **')
                        else:
                            no_improve += 1
                            print(f'    no improve {no_improve}/{PATIENCE}')
                            if no_improve >= PATIENCE:
                                print(f'  Early stopping at step {global_step}')
                                plot_training()
                                print(f'Training complete. Best val_acc: {best_val_acc:.4f}')
                                return
                        if global_step % 1000 == 0:
                            plot_training()

    plot_training()
    print(f'Training complete. Best val_acc: {best_val_acc:.4f}')


# ─── Validation ───────────────────────────────────────────────────────────

def validate(model, global_step, epoch):
    from torch.utils.data import Dataset as ValDS, DataLoader as ValDL

    val_data = []
    with open('data/combined/val.jsonl') as f:
        for line in f:
            line = line.strip()
            if line:
                val_data.append(json.loads(line))

    valid_idx = [i for i, item in enumerate(val_data) if item.get('input_ids') and item.get('target_ids')]
    valid_idx = valid_idx[:5000]

    class ValSet(ValDS):
        def __len__(self): return len(valid_idx)
        def __getitem__(self, idx):
            item = val_data[valid_idx[idx]]
            ids = (item['input_ids'] + item['target_ids'])[:1024]
            mask = [0]*len(item['input_ids']) + [1]*len(item['target_ids'])
            return {
                'input_ids': torch.tensor(ids[:1024], dtype=torch.long),
                'mask': torch.tensor(mask[:1024], dtype=torch.float),
                'mode': item.get('mode','plan'),
                'domain': item.get('domain','unknown'),
            }

    val_loader = ValDL(ValSet(), batch_size=4, shuffle=False, collate_fn=collate_fn)
    model.model.eval()
    total_loss, total_acc, n = 0.0, 0.0, 0
    print(f'  Validating ({len(val_loader)} batches)...')
    val_start = time.time()

    with torch.no_grad():
        for vids, vmask, vmodes, _ in val_loader:
            vtargs = vids.clone()
            vtargs[vtargs == PAD] = -100
            v_is_build = all(m == 'build' for m in vmodes)
            vlogits, _ = model.model(vids, mode='build' if v_is_build else 'plan')
            vl, va = compute_loss(vlogits, vtargs, vmask, smoothing=0.0)
            total_loss += vl.item()
            total_acc += va.item()
            n += 1

    model.model.train()
    avg_loss = total_loss / max(n, 1)
    avg_acc = total_acc / max(n, 1)
    val_ppl = math.exp(min(avg_loss, 20))
    val_time = time.time() - val_start
    print(f'    val_complete: {val_time:.0f}s')
    return avg_loss, avg_acc, val_ppl


if __name__ == '__main__':
    main()
