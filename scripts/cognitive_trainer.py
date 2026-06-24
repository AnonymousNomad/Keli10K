#!/usr/bin/env python3
"""Cognitive pipeline trainer for Keli10K — 7-level curriculum, streaming, per-domain tracking."""
import sys, os, json, math, time, csv, signal
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from snca_tokenizer import SNCATokenizer
from snca_config import SNCACfg
from keli_10k import Keli10KModel

PAD = 0
BOS = 2
LR_BASE = 1e-4
LR_MIN = 1e-6
WARMUP = 500
BATCH_SIZE = 4
ACCUM = 1
VAL_EVERY = 100
MAX_MINI_EPOCHS = 2
NUM_CHUNKS = 15
EXAMPLES_PER_MINI_EPOCH = 2000
CKPT_EVERY = 500
KEEP_TOP_CKPTS = 5

LEVELS = list(range(1, 8))
DOMAINS = [
    'reasoning', 'metacognition', 'architecture', 'code', 'web',
    'backend', 'games', 'graphics', 'mobile', 'algorithms',
    'debug', 'synthesis', 'security', 'math', 'masters',
]

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHUNKS_DIR = BASE_DIR / 'data' / 'chunks'
VAL_DIR = BASE_DIR / 'data' / 'chunks_val'
CHECKPOINT_DIR = BASE_DIR / 'checkpoints'
LOG_DIR = BASE_DIR / 'logs'
CHECKPOINT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
CSV_PATH = LOG_DIR / 'cognitive_log.csv'


# ─── Streaming Chunk Dataset ──────────────────────────────────────────────

class StreamingChunkDataset(Dataset):
    def __init__(self, path, start=0, count=EXAMPLES_PER_MINI_EPOCH, max_len=384):
        self.max_len = max_len
        self.items = []
        tok = SNCATokenizer()
        with open(path) as f:
            for i, line in enumerate(f):
                if i < start:
                    continue
                if len(self.items) >= count:
                    break
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                input_ids = tok.encode(item.get('input', ''), bos=True, eos=False)
                target_ids = tok.encode(item.get('target', ''), bos=True, eos=True)
                if not input_ids or not target_ids:
                    continue
                self.items.append({
                    'input_ids': input_ids,
                    'target_ids': target_ids,
                    'cognitive_level': int(item.get('cognitive_level', 1)),
                    'domain': item.get('domain', 'unknown'),
                })
        print(f'  Loaded {len(self.items)} examples from {Path(path).name} (offset={start})')

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        item = self.items[idx]
        ids = (item['input_ids'] + item['target_ids'])[:self.max_len]
        mask = [0] * len(item['input_ids']) + [1] * len(item['target_ids'])
        mask = mask[:self.max_len]
        return {
            'input_ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.float),
            'cognitive_level': item['cognitive_level'],
            'domain': item['domain'],
        }


# ─── Collate ──────────────────────────────────────────────────────────────

def collate_fn(batch):
    input_ids = [b['input_ids'] for b in batch]
    masks = [b['mask'] for b in batch]
    levels = [b['cognitive_level'] for b in batch]
    domains = [b['domain'] for b in batch]
    max_len = max(len(ids) for ids in input_ids)
    pids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    pms = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (ids, m) in enumerate(zip(input_ids, masks)):
        pids[i, :len(ids)] = ids
        pms[i, :len(m)] = torch.as_tensor(m, dtype=torch.float)
    return pids, pms, levels, domains


# ─── Loss ─────────────────────────────────────────────────────────────────

def compute_loss(logits, targets, mask, smoothing=0.1):
    shift_logits = logits[:, :-1, :].contiguous()
    shift_targets = targets[:, 1:].contiguous()
    shift_mask = mask[:, 1:].contiguous()
    V = logits.size(-1)

    valid = (shift_targets != -100)
    shift_targets_safe = shift_targets.clamp(min=0)
    shift_mask = shift_mask * valid.float()

    if smoothing > 0:
        smooth_loss = -F.log_softmax(shift_logits, dim=-1)
        smooth_targets = torch.full_like(smooth_loss, smoothing / (V - 1))
        smooth_targets.scatter_(-1, shift_targets_safe.unsqueeze(-1), 1 - smoothing)
        loss = (smooth_loss * smooth_targets).sum(-1)
    else:
        loss = F.cross_entropy(shift_logits.view(-1, V), shift_targets_safe.view(-1), reduction='none')
        loss = loss.view(shift_logits.size(0), -1)

    masked_loss = (loss * shift_mask).sum() / (shift_mask.sum() + 1e-8)
    preds = shift_logits.argmax(dim=-1)
    correct = ((preds == shift_targets_safe) * shift_mask.bool()).sum().float()
    acc = correct / (shift_mask.sum() + 1e-8)
    return masked_loss, acc


# ─── LR Scheduler (warmup-cosine + ReduceLROnPlateau) ─────────────────────

class LRScheduler:
    def __init__(self, optimizer, warmup=WARMUP, base_lr=LR_BASE, min_lr=LR_MIN):
        self.opt = optimizer
        self.warmup = warmup
        self.base_lr = base_lr
        self.min_lr = min_lr
        self.step_count = 0
        self.total_steps = None
        self._best_loss = float('inf')
        self._plateau_count = 0

    def set_total_steps(self, n):
        self.total_steps = n

    def step(self, val_loss=None):
        self.step_count += 1
        s = self.step_count
        if s < self.warmup:
            lr = self.base_lr * (s + 1) / (self.warmup + 1)
        elif self.total_steps:
            progress = (s - self.warmup) / max(self.total_steps - self.warmup, 1)
            lr = self.min_lr + 0.5 * (self.base_lr - self.min_lr) * (1 + math.cos(math.pi * progress))
        else:
            lr = self.base_lr

        if val_loss is not None:
            if val_loss < self._best_loss - 1e-4:
                self._best_loss = val_loss
                self._plateau_count = 0
            else:
                self._plateau_count += 1
                if self._plateau_count >= 3:
                    lr = max(lr * 0.5, self.min_lr)
                    print(f'    ReduceLROnPlateau: lr -> {lr:.2e}')
                    self._plateau_count = 0
                    self._best_loss = val_loss

        for pg in self.opt.param_groups:
            pg['lr'] = lr
        return lr


# ─── Checkpoint Manager ──────────────────────────────────────────────────

class CheckpointManager:
    def __init__(self, directory=CHECKPOINT_DIR, keep_top=KEEP_TOP_CKPTS):
        self.dir = Path(directory)
        self.keep_top = keep_top

    def save(self, model, optimizer, step, val_acc, val_loss):
        fname = f'cognitive_step_{step}.pt'
        path = self.dir / fname
        torch.save({
            'model_state': model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'step': step,
            'val_acc': val_acc,
            'val_loss': val_loss,
        }, path)
        self._prune()
        return path

    def _prune(self):
        ckpts = sorted(self.dir.glob('cognitive_step_*.pt'), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in ckpts[self.keep_top:]:
            old.unlink()

    def save_partial(self, model, optimizer, step, val_acc, val_loss):
        path = self.dir / 'cognitive_partial.pt'
        torch.save({
            'model_state': model.state_dict(),
            'optimizer_state': optimizer.state_dict(),
            'step': step,
            'val_acc': val_acc,
            'val_loss': val_loss,
        }, path)
        print(f'  Partial checkpoint saved: {path}')


# ─── Per-Level / Per-Domain Tracker ──────────────────────────────────────

class MetricsTracker:
    def __init__(self):
        self.level_correct = {l: 0.0 for l in LEVELS}
        self.level_total = {l: 0.0 for l in LEVELS}
        self.domain_correct = {d: 0.0 for d in DOMAINS}
        self.domain_total = {d: 0.0 for d in DOMAINS}

    def update(self, levels, domains, correct_counts, total_counts):
        for lvl in set(levels):
            idxs = [i for i, v in enumerate(levels) if v == lvl]
            self.level_correct[lvl] += sum(correct_counts[i] for i in idxs)
            self.level_total[lvl] += sum(total_counts[i] for i in idxs)
        for dom in set(domains):
            if dom not in self.domain_correct:
                continue
            idxs = [i for i, v in enumerate(domains) if v == dom]
            self.domain_correct[dom] += sum(correct_counts[i] for i in idxs)
            self.domain_total[dom] += sum(total_counts[i] for i in idxs)

    def level_acc(self):
        return {l: (self.level_correct[l] / max(self.level_total[l], 1)) for l in LEVELS}

    def domain_acc(self):
        return {d: (self.domain_correct[d] / max(self.domain_total[d], 1)) for d in DOMAINS}


# ─── Validation ──────────────────────────────────────────────────────────

def validate(model, step, cur_info, ckpt_mgr, csv_writer):
    model.model.eval()
    val_tracker = MetricsTracker()
    total_loss, total_acc, n_batches = 0.0, 0.0, 0

    print(f'  Validating (step {step})...')
    val_start = time.time()

    with torch.no_grad():
        for chunk_idx in range(1, NUM_CHUNKS + 1):
            val_path = VAL_DIR / f'chunk_{chunk_idx:02d}.jsonl'
            if not val_path.exists():
                continue
            val_ds = StreamingChunkDataset(val_path, start=0, count=200)
            if len(val_ds) == 0:
                continue
            val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)
            for vids, vmask, vlevels, vdomains in val_loader:
                vtargs = vids.clone()
                vtargs[vtargs == PAD] = -100
                vlogits, _ = model.model(vids, mode='build')
                vl, va = compute_loss(vlogits, vtargs, vmask, smoothing=0.0)
                total_loss += vl.item()
                total_acc += va.item()
                n_batches += 1

                shift_logits = vlogits[:, :-1, :].contiguous()
                shift_targets = vtargs[:, 1:].contiguous()
                shift_mask = vmask[:, 1:].contiguous()
                valid = shift_targets != -100
                shift_targets_safe = shift_targets.clamp(min=0)
                shift_mask = shift_mask * valid.float()
                preds = shift_logits.argmax(dim=-1)
                batch_correct = []
                batch_total = []
                for b in range(vids.size(0)):
                    sm = shift_mask[b].bool()
                    batch_correct.append(((preds[b] == shift_targets_safe[b]) * sm).sum().item())
                    batch_total.append(sm.sum().item())
                val_tracker.update(vlevels, vdomains, batch_correct, batch_total)

    model.model.train()
    avg_loss = total_loss / max(n_batches, 1)
    avg_acc = total_acc / max(n_batches, 1)
    val_ppl = math.exp(min(avg_loss, 20))
    val_time = time.time() - val_start
    print(f'    val_complete: {val_time:.0f}s | loss={avg_loss:.4f} acc={avg_acc:.4f} ppl={val_ppl:.2f}')

    level_accs = val_tracker.level_acc()
    domain_accs = val_tracker.domain_acc()
    print(f'    Per-level acc: {", ".join(f"L{l}:{level_accs[l]*100:.1f}%" for l in LEVELS)}')
    top5 = DOMAINS[:5]
    print(f'    Per-domain acc: {", ".join(f"{d}:{domain_accs[d]*100:.1f}%" for d in top5)}...')

    csv_writer.writerow({
        'step': step, 'chunk': cur_info.get('chunk', ''),
        'level': cur_info.get('level', ''), 'domain': 'all',
        'train_loss': '', 'train_acc': '',
        'val_loss': f'{avg_loss:.6f}', 'val_acc': f'{avg_acc:.6f}', 'lr': '',
    })
    for l in LEVELS:
        csv_writer.writerow({
            'step': step, 'chunk': cur_info.get('chunk', ''),
            'level': l, 'domain': 'all',
            'train_loss': '', 'train_acc': '',
            'val_loss': '', 'val_acc': f'{level_accs[l]*100:.2f}', 'lr': '',
        })
    for d in DOMAINS:
        csv_writer.writerow({
            'step': step, 'chunk': cur_info.get('chunk', ''),
            'level': '', 'domain': d,
            'train_loss': '', 'train_acc': '',
            'val_loss': '', 'val_acc': f'{domain_accs[d]*100:.2f}', 'lr': '',
        })

    return avg_loss, avg_acc, val_ppl


# ─── Curriculum Schedule ─────────────────────────────────────────────────

def get_curriculum_level(chunk_idx, mini_epoch):
    total_units = NUM_CHUNKS * MAX_MINI_EPOCHS
    unit = (chunk_idx - 1) * MAX_MINI_EPOCHS + (mini_epoch - 1)
    progress = unit / max(total_units - 1, 1)
    return min(7, max(1, int(progress * 7) + 1))


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    cfg = SNCACfg()
    model = Keli10KModel(cfg)
    n_params = sum(p.numel() for p in model.model.parameters())
    print(f'Cognitive Trainer | Model: {n_params/1e6:.2f}M params')

    optimizer = torch.optim.AdamW(
        model.model.parameters(), lr=LR_BASE, weight_decay=0.01, betas=(0.9, 0.95)
    )
    lr_sched = LRScheduler(optimizer)
    ckpt_mgr = CheckpointManager()

    csv_f = open(CSV_PATH, 'w', newline='')
    csv_writer = csv.DictWriter(
        csv_f, fieldnames=['step', 'chunk', 'level', 'domain',
                           'train_loss', 'train_acc', 'val_loss', 'val_acc', 'lr']
    )
    csv_writer.writeheader()
    csv_f.flush()

    global_step = 0
    best_val_acc = 0.0
    interrupted = False
    step_loss = 0.0

    def signal_handler(sig, frame):
        nonlocal interrupted
        print('\n  KeyboardInterrupt received, saving partial checkpoint...')
        interrupted = True

    signal.signal(signal.SIGINT, signal_handler)

    total_steps_estimate = NUM_CHUNKS * MAX_MINI_EPOCHS * (EXAMPLES_PER_MINI_EPOCH // BATCH_SIZE // ACCUM)
    lr_sched.set_total_steps(total_steps_estimate)

    for chunk_idx in range(1, NUM_CHUNKS + 1):
        if interrupted:
            break
        chunk_path = CHUNKS_DIR / f'chunk_{chunk_idx:02d}.jsonl'
        if not chunk_path.exists():
            print(f'  Chunk {chunk_path.name} not found, skipping')
            continue

        for mini_epoch in range(1, MAX_MINI_EPOCHS + 1):
            if interrupted:
                break
            curriculum_level = get_curriculum_level(chunk_idx, mini_epoch)
            start_line = (mini_epoch - 1) * EXAMPLES_PER_MINI_EPOCH

            print(f'\nChunk {chunk_idx}/{NUM_CHUNKS} | Mini-epoch {mini_epoch}/{MAX_MINI_EPOCHS} | Level {curriculum_level} | Offset {start_line}')

            dataset = StreamingChunkDataset(chunk_path, start=start_line, count=EXAMPLES_PER_MINI_EPOCH)
            if len(dataset) == 0:
                continue
            loader = DataLoader(
                dataset, batch_size=BATCH_SIZE, shuffle=True,
                collate_fn=collate_fn, drop_last=True
            )

            model.model.train()
            accum_loss, accum_acc, accum_count = 0.0, 0.0, 0
            epoch_start = time.time()

            for batch_idx, (input_ids, mask, levels, domains) in enumerate(loader):
                if interrupted:
                    break
                lr = lr_sched.step()
                targets = input_ids.clone()
                targets[targets == PAD] = -100

                logits, _ = model.model(input_ids, mode='build')
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
                        print(f'  Step {global_step:6d} | loss={step_loss:.4f} acc={step_acc:.4f} ppl={ppl:.2f} lr={lr:.2e} [{chunk_idx}.{mini_epoch}] ({elapsed:.1f}s)')
                        epoch_start = time.time()

                    csv_writer.writerow({
                        'step': global_step, 'chunk': chunk_idx,
                        'level': curriculum_level, 'domain': 'all',
                        'train_loss': f'{step_loss:.6f}', 'train_acc': f'{step_acc:.6f}',
                        'val_loss': '', 'val_acc': '', 'lr': f'{lr:.2e}',
                    })

                    if global_step % VAL_EVERY == 0:
                        val_result = validate(
                            model, global_step,
                            {'chunk': chunk_idx, 'level': curriculum_level},
                            ckpt_mgr, csv_writer
                        )
                        if val_result:
                            val_loss, val_acc, val_ppl = val_result
                            print(f'  >> val_loss={val_loss:.4f} val_acc={val_acc:.4f} val_ppl={val_ppl:.2f}')
                            lr_sched.step(val_loss=val_loss)
                            if val_acc > best_val_acc:
                                best_val_acc = val_acc
                                print(f'    ** NEW BEST: {val_acc:.4f} **')

                    if global_step % CKPT_EVERY == 0:
                        path = ckpt_mgr.save(model.model, optimizer, global_step, best_val_acc, step_loss)
                        print(f'  Checkpoint saved: {path}')

                    if global_step % 1000 == 0:
                        csv_f.flush()

            csv_f.flush()

    if global_step > 0:
        if interrupted:
            ckpt_mgr.save_partial(model.model, optimizer, global_step, best_val_acc, step_loss)
        else:
            ckpt_mgr.save(model.model, optimizer, global_step, best_val_acc, step_loss)
            print(f'Final checkpoint saved at step {global_step}')

    csv_f.close()
    print(f'Training complete. Best val_acc: {best_val_acc:.4f}')
    print(f'Logs: {CSV_PATH}')


if __name__ == '__main__':
    main()
