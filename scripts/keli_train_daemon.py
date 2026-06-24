#!/usr/bin/env python3
"""Keli training daemon — fast logging, continuous training."""
import sys, os, json, torch, math, time, signal
torch.set_num_threads(8)
sys.path.insert(0, '/tmp/opencode/snca')
sys.path.insert(0, '/tmp/opencode/snca/scripts')
from snca_config import SNCACfg
from keli_10k import Keli10KModel
from trainer import SwarmDataset, collate_batch, compute_loss_and_acc
from torch.utils.data import DataLoader

cfg = SNCACfg(); PAD = 0; BATCH_SIZE = 16
LOG_FILE = 'training_daemon.log'; CKPT_DIR = 'checkpoints'

def log(msg):
    with open(LOG_FILE, 'a') as f: f.write(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {msg}\n')
    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] {msg}', flush=True)

log("Daemon starting...")
with open('data/combined/train.jsonl') as f: train_data = [json.loads(l) for l in f if l.strip()]
with open('data/advanced/val.jsonl') as f: val_data = [json.loads(l) for l in f if l.strip()]
log(f"Train: {len(train_data)} Val: {len(val_data)}")

train_ds = SwarmDataset(train_data, max_len=384)
val_ds = SwarmDataset(val_data, max_len=384)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_batch)
val_loader = DataLoader(val_ds, batch_size=32, shuffle=False, collate_fn=collate_batch)

ckpt_path = f'{CKPT_DIR}/keli_best.pt'
if os.path.exists(ckpt_path):
    ckpt = torch.load(ckpt_path, map_location='cpu')
    model = Keli10KModel(cfg)
    model.model.load_state_dict(ckpt['model_state'], strict=False)
    start_step = ckpt.get('step', 0); best_val_acc = ckpt.get('val_acc', 0.0)
    log(f"Resumed step {start_step}, best_val_acc={best_val_acc*100:.2f}%")
else:
    model = Keli10KModel(cfg); start_step = 0; best_val_acc = 0.0
    log(f"Fresh model: {sum(p.numel() for p in model.model.parameters())/1e6:.2f}M")

model.model.train()
optimizer = torch.optim.AdamW(model.model.parameters(), lr=5e-4, weight_decay=0.05, betas=(0.9, 0.95))
if os.path.exists(ckpt_path) and 'optimizer_state' in ckpt:
    try: optimizer.load_state_dict(ckpt['optimizer_state'])
    except: pass

global_step = start_step
total_steps = len(train_loader) * 30
warmup_steps = min(500, total_steps // 10)
log(f"Total steps/epoch: {len(train_loader)}, warmup: {warmup_steps}")

running_loss = 0.0; running_acc = 0.0; running_count = 0
t0 = time.time(); val_count = 0

for epoch in range(30):
    model.model.train()
    for batch_idx, (input_ids, mask, modes) in enumerate(train_loader):
        lr = 5e-4 * (global_step+1)/(warmup_steps+1) if global_step < warmup_steps else 5e-4 * 0.5 * (1.0+math.cos(math.pi*(global_step-warmup_steps)/max(total_steps-warmup_steps,1)))
        for pg in optimizer.param_groups: pg['lr'] = lr
        targets = input_ids.clone(); targets[targets == PAD] = -100
        is_build = all(m == 'build' for m in modes)
        logits, _ = model.model(input_ids, mode='build' if is_build else 'plan')
        loss, acc = compute_loss_and_acc(logits, targets, mask)
        loss.backward(); running_loss += loss.item(); running_acc += acc.item(); running_count += 1
        if (batch_idx + 1) % 2 == 0:
            torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
            optimizer.step(); optimizer.zero_grad(); global_step += 1
            if global_step % 10 == 0:
                elapsed = time.time() - t0
                log(f"step {global_step:5d} loss={running_loss/running_count:.4f} acc={running_acc/running_count*100:.2f}% lr={lr:.2e} ({elapsed/3600:.1f}h)")
                running_loss = 0.0; running_acc = 0.0; running_count = 0
            if global_step % 100 == 0:
                model.model.eval(); v_losses, v_accs = [], []
                t_val = time.time()
                with torch.no_grad():
                    for v_ids, v_mask, v_modes in val_loader:
                        v_targets = v_ids.clone(); v_targets[v_targets == PAD] = -100
                        v_is_build = all(m == 'build' for m in v_modes)
                        v_logits, _ = model.model(v_ids, mode='build' if v_is_build else 'plan')
                        v_l, v_a = compute_loss_and_acc(v_logits, v_targets, v_mask)
                        v_losses.append(v_l.item()); v_accs.append(v_a.item())
                avg_val = sum(v_accs)/max(len(v_accs),1)
                log(f"  VALIDATION acc={avg_val*100:.2f}% best={best_val_acc*100:.2f}% ({time.time()-t_val:.0f}s)")
                if avg_val > best_val_acc:
                    best_val_acc = avg_val
                    torch.save({'model_state': model.model.state_dict(), 'optimizer_state': optimizer.state_dict(), 'step': global_step, 'val_acc': avg_val}, f'{CKPT_DIR}/keli_best.pt')
                    log(f"  ** NEW BEST: {avg_val*100:.2f}% **")
                    if avg_val >= 0.90:
                        log(f"  ★ 90% TARGET REACHED at step {global_step}!")
                        torch.save({'model_state': model.model.state_dict(), 'step': global_step, 'val_acc': avg_val}, f'{CKPT_DIR}/keli_90pct.pt')
                torch.save({'model_state': model.model.state_dict(), 'step': global_step, 'val_acc': best_val_acc}, f'{CKPT_DIR}/keli_latest.pt')
                model.model.train(); val_count += 1
