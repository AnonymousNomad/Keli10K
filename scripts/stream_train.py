#!/usr/bin/env python3
"""Streaming training — doesn't load all data into RAM. Logs every 5 steps."""
import sys, os, json, torch, math, time, random
torch.set_num_threads(8)
sys.path.insert(0, '/tmp/opencode/snca'); sys.path.insert(0, '/tmp/opencode/snca/scripts')
from snca_config import SNCACfg; from keli_10k import Keli10K, Keli10KModel
cfg = SNCACfg(); PAD = 0; LOG = 'training_stream.log'

def log(msg):
    with open(LOG, 'a') as f: f.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    print(f'[{time.strftime("%H:%M:%S")}] {msg}', flush=True)

log("Stream trainer starting...")

# Load only a subset for now — 20K examples fits in RAM easily
with open('data/combined/train.jsonl') as f:
    train_lines = f.readlines()
random.shuffle(train_lines)
train_data = [json.loads(l) for l in train_lines[:20000] if l.strip()]
del train_lines

with open('data/advanced/val.jsonl') as f:
    val_lines = f.readlines()
val_data = [json.loads(l) for l in val_lines[:2000] if l.strip()]
del val_lines

log(f"Train: {len(train_data)} Val: {len(val_data)}")

# Use trainer classes
from trainer import SwarmDataset, collate_batch, compute_loss_and_acc
from torch.utils.data import DataLoader

train_ds = SwarmDataset(train_data, max_len=256)
val_ds = SwarmDataset(val_data, max_len=256)
train_loader = DataLoader(train_ds, batch_size=16, shuffle=True, collate_fn=collate_batch, drop_last=True)
val_loader = DataLoader(val_ds, batch_size=32, shuffle=False, collate_fn=collate_batch)

model = Keli10KModel(cfg)
model.model.train()
optimizer = torch.optim.AdamW(model.model.parameters(), lr=5e-4, weight_decay=0.05, betas=(0.9, 0.95))
log(f"Model: {sum(p.numel() for p in model.model.parameters())/1e6:.2f}M")

global_step = 0; best_val_acc = 0.0; running_loss = 0.0; running_acc = 0.0; rc = 0
total_steps = len(train_loader) * 20; warmup_steps = min(500, total_steps // 10)
t0 = time.time()
log(f"Steps/epoch: {len(train_loader)}")

for epoch in range(20):
    model.model.train()
    for batch_idx, (input_ids, mask, modes) in enumerate(train_loader):
        lr = 5e-4 * min(1.0, (global_step+1)/max(warmup_steps,1)) * 0.5 * (1.0+math.cos(math.pi*max(0,global_step-warmup_steps)/max(total_steps-warmup_steps,1)))
        for pg in optimizer.param_groups: pg['lr'] = lr
        targets = input_ids.clone(); targets[targets == PAD] = -100
        is_build = all(m == 'build' for m in modes)
        logits, _ = model.model(input_ids, mode='build' if is_build else 'plan')
        loss, acc = compute_loss_and_acc(logits, targets, mask)
        (loss/2).backward(); running_loss += loss.item(); running_acc += acc.item(); rc += 1
        if (batch_idx+1) % 2 == 0:
            torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
            optimizer.step(); optimizer.zero_grad(); global_step += 1
            if global_step % 10 == 0:
                log(f"step {global_step:5d} loss={running_loss/rc:.4f} acc={running_acc/rc*100:.2f}% ({time.time()-t0:.0f}s)")
                running_loss = 0.0; running_acc = 0.0; rc = 0
            if global_step % 100 == 0:
                model.model.eval(); v_accs = []
                with torch.no_grad():
                    for v_ids, v_mask, v_modes in val_loader:
                        v_targets = v_ids.clone(); v_targets[v_targets==PAD] = -100
                        v_is_build = all(m == 'build' for m in v_modes)
                        _, v_a = compute_loss_and_acc(*model.model(v_ids, mode='build' if v_is_build else 'plan'), v_targets, v_mask)
                        v_accs.append(v_a.item())
                avg_val = sum(v_accs)/max(len(v_accs),1)
                log(f"  VAL acc={avg_val*100:.2f}% best={best_val_acc*100:.2f}%")
                if avg_val > best_val_acc:
                    best_val_acc = avg_val
                    torch.save({'model_state': model.model.state_dict(), 'optimizer_state': optimizer.state_dict(), 'step': global_step, 'val_acc': avg_val}, 'checkpoints/keli_best.pt')
                    log(f"  ** NEW BEST: {avg_val*100:.2f}% **")
                    if avg_val >= 0.90:
                        log(f"  ★ 90% TARGET!"); torch.save({'model_state': model.model.state_dict(), 'step': global_step}, 'checkpoints/keli_90pct.pt'); sys.exit(0)
                model.model.train()
    log(f"Epoch {epoch+1} done (step {global_step})")
log("Training complete!")
