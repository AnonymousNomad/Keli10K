#!/usr/bin/env python3
"""Memory-efficient streaming training — stays alive, logs everything."""
import sys, os, json, torch, math, time, gc, random
torch.set_num_threads(4)
sys.path.insert(0, '/tmp/opencode/snca'); sys.path.insert(0, '/tmp/opencode/snca/scripts')
from snca_config import SNCACfg; from keli_10k import Keli10KModel
from trainer import SwarmDataset, collate_batch, compute_loss_and_acc
from torch.utils.data import DataLoader, IterableDataset

LOG = '/tmp/opencode/snca/train_survive.log'
def log(m):
    t = time.strftime("%H:%M:%S")
    with open(LOG, 'a') as f: f.write(f'[{t}] {m}\n')
    print(f'[{t}] {m}', flush=True)

log("=== SURVIVABLE TRAINING STARTED ===")

# Load minimal data — only what we need
with open('data/combined/train.jsonl') as f: all_train = [json.loads(l) for l in f if l.strip()]
with open('data/advanced/val.jsonl') as f: all_val = [json.loads(l) for l in f if l.strip()]
random.shuffle(all_train)
train = all_train[:10000]; val = all_val[:1000]
del all_train, all_val; gc.collect()
log(f"Data: {len(train)} train, {len(val)} val")

model = Keli10KModel(SNCACfg())
model.model.train()
optim = torch.optim.AdamW(model.model.parameters(), lr=3e-4, weight_decay=0.1)
log(f"Model: {sum(p.numel() for p in model.model.parameters())/1e6:.2f}M")

train_ds = SwarmDataset(train, max_len=256)
val_ds = SwarmDataset(val, max_len=256)
train_loader = DataLoader(train_ds, batch_size=12, shuffle=True, collate_fn=collate_batch, num_workers=0)
val_loader = DataLoader(val_ds, batch_size=24, shuffle=False, collate_fn=collate_batch)
del train, val; gc.collect()
log(f"Batches: {len(train_loader)} train, {len(val_loader)} val")

step = 0; best_val = 0.0; rl = 0.0; ra = 0.0; rc = 0; t0 = time.time()
warmup = 200; total_steps = len(train_loader) * 15
log(f"Warmup: {warmup}, total steps expected: {total_steps}")

for epoch in range(15):
    model.model.train()
    for ids, mask, modes in train_loader:
        targets = ids.clone(); targets[targets==0] = -100
        is_build = all(m == 'build' for m in modes)
        logits, _ = model.model(ids, mode='build' if is_build else 'plan')
        loss, acc = compute_loss_and_acc(logits, targets, mask)
        (loss/2).backward(); rl += loss.item(); ra += acc.item(); rc += 1
        if rc >= 2:
            torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
            lr = 3e-4 * (step+1)/warmup if step < warmup else 3e-4 * 0.5 * (1+math.cos(math.pi*(step-warmup)/max(total_steps-warmup,1)))
            for pg in optim.param_groups: pg['lr'] = lr
            optim.step(); optim.zero_grad(); step += 1
            if step % 10 == 0:
                log(f"step{step:5d} loss={rl/rc:.4f} acc={ra/rc*100:.2f}% lr={lr:.2e} mem={os.popen('free -m|grep Mem').read().split()[3] if hasattr(os,'popen') else '?'}MB ({time.time()-t0:.0f}s)")
                rl=0; ra=0; rc=0; gc.collect()
            if step % 50 == 0:
                model.model.eval(); va = []
                with torch.no_grad():
                    for vi, vm, vmo in val_loader:
                        vt = vi.clone(); vt[vt==0] = -100
                        vb = all(mo == 'build' for mo in vmo)
                        _, va2 = compute_loss_and_acc(*model.model(vi, mode='build' if vb else 'plan'), vt, vm)
                        va.append(va2.item())
                avgv = sum(va)/max(len(va),1)
                log(f"  VAL acc={avgv*100:.2f}% best={best_val*100:.2f}%")
                if avgv > best_val:
                    best_val = avgv; torch.save({'model_state': model.model.state_dict(), 'step': step, 'val_acc': avgv}, 'checkpoints/keli_best.pt')
                    log(f"  ** NEW BEST: {avgv*100:.2f}% **")
                    if avgv >= 0.90: log("★ 90% REACHED"); torch.save({'model_state': model.model.state_dict(), 'step': step}, 'checkpoints/keli_90pct.pt'); sys.exit(0)
                model.model.train(); gc.collect()
    log(f"Epoch {epoch+1} done")
log("Training complete")
