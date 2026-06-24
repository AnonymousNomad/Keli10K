#!/usr/bin/env python3
"""Proper training loop with validation to reach 90%+ accuracy."""
import sys, os, json, torch, math, time
sys.path.insert(0, '/tmp/opencode/snca')
sys.path.insert(0, '/tmp/opencode/snca/scripts')
torch.set_num_threads(8)

from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from keli_10k import Keli10K
from trainer import SwarmDataset, collate_batch, compute_loss_and_acc
from torch.utils.data import DataLoader

cfg = SNCACfg()
tok = SNCATokenizer()
PAD = 0
BATCH_SIZE = 32
VAL_BATCH_SIZE = 64
MAX_LEN = 512
PRINT_EVERY = 50
VAL_EVERY = 200
CKPT_DIR = 'checkpoints'

os.makedirs(CKPT_DIR, exist_ok=True)

def load_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line: data.append(json.loads(line))
    return data

print("Loading data...")
train_data = load_jsonl('data/combined/train.jsonl')
val_data = load_jsonl('data/advanced/val.jsonl')
print(f"Train: {len(train_data)} | Val: {len(val_data)}")

train_ds = SwarmDataset(train_data, max_len=MAX_LEN)
val_ds = SwarmDataset(val_data, max_len=MAX_LEN)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_batch, num_workers=0)
val_loader = DataLoader(val_ds, batch_size=VAL_BATCH_SIZE, shuffle=False, collate_fn=collate_batch, num_workers=0)

# Model
ckpt_path = f'{CKPT_DIR}/keli_navy_latest.pt'
if os.path.exists(ckpt_path):
    ckpt = torch.load(ckpt_path, map_location='cpu')
    n_bots = ckpt['model_state']['nanobot_embed.weight'].shape[0]
    start_step = ckpt.get('step', 0)
    best_val_acc = ckpt.get('best_val_acc', 0.0)
    print(f"Resuming from step {start_step}, best_val_acc={best_val_acc:.4f}")
else:
    n_bots = 100000
    start_step = 0
    best_val_acc = 0.0
    print(f"Starting fresh with {n_bots:,} nanobots")

model = Keli10K(
    vocab_size=cfg.vocab_size, dim=cfg.d_model, n_heads=cfg.n_heads,
    n_layers=cfg.n_layers, ffn_hidden=cfg.d_ff, max_len=cfg.max_len,
    n_nanobots=n_bots, nanobot_dim=200, n_comm_rounds=5, dropout=cfg.dropout,
)
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1, betas=(0.9, 0.95))

if os.path.exists(ckpt_path):
    model.load_state_dict(ckpt['model_state'], strict=True)
    try:
        optimizer.load_state_dict(ckpt['optimizer_state'])
    except: pass

model.train()
total_params = sum(p.numel() for p in model.parameters())
print(f"Model: {total_params/1e6:.2f}M params, {n_bots:,} nanobots")

global_step = start_step
total_steps = len(train_loader) * 20
warmup_steps = min(1000, total_steps // 10)

def get_lr(step):
    if step < warmup_steps: return 3e-4 * (step + 1) / (warmup_steps + 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    return 3e-4 * 0.5 * (1.0 + math.cos(math.pi * progress))

t_start = time.time()
no_improve = 0

for epoch in range(20):
    model.train()
    accum_loss, accum_acc, accum_count = 0.0, 0.0, 0

    for batch_idx, (input_ids, mask, modes) in enumerate(train_loader):
        lr = get_lr(global_step)
        for pg in optimizer.param_groups:
            pg['lr'] = lr

        targets = input_ids.clone()
        targets[targets == PAD] = -100
        is_build = all(m == 'build' for m in modes)
        logits, _ = model(input_ids, mode='build' if is_build else 'plan')
        loss, acc = compute_loss_and_acc(logits, targets, mask)

        loss.backward()
        accum_loss += loss.item()
        accum_acc += acc.item()
        accum_count += 1

        if (batch_idx + 1) % 2 == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()

            global_step += 1

            if global_step % PRINT_EVERY == 0:
                avg_loss = accum_loss / accum_count
                avg_acc = accum_acc / accum_count
                ppl = math.exp(min(avg_loss, 20))
                elapsed = time.time() - t_start
                print(f"[{elapsed/3600:.1f}h] step {global_step:5d} | loss={avg_loss:.4f} acc={avg_acc:.4f} ppl={ppl:.2f} lr={lr:.2e}", flush=True)
                accum_loss, accum_acc, accum_count = 0.0, 0.0, 0

            if global_step % VAL_EVERY == 0:
                model.eval()
                val_losses, val_accs = [], []
                with torch.no_grad():
                    for v_ids, v_mask, v_modes in val_loader:
                        v_targets = v_ids.clone()
                        v_targets[v_targets == PAD] = -100
                        v_is_build = all(m == 'build' for m in v_modes)
                        v_logits, _ = model(v_ids, mode='build' if v_is_build else 'plan')
                        v_l, v_a = compute_loss_and_acc(v_logits, v_targets, v_mask)
                        val_losses.append(v_l.item())
                        val_accs.append(v_a.item())

                avg_val_loss = sum(val_losses) / max(len(val_losses), 1)
                avg_val_acc = sum(val_accs) / max(len(val_accs), 1)
                val_ppl = math.exp(min(avg_val_loss, 20))
                print(f"  VAL: loss={avg_val_loss:.4f} acc={avg_val_acc*100:.2f}% ppl={val_ppl:.2f}", flush=True)

                if avg_val_acc > best_val_acc:
                    best_val_acc = avg_val_acc
                    no_improve = 0
                    torch.save({
                        'model_state': model.state_dict(),
                        'optimizer_state': optimizer.state_dict(),
                        'step': global_step,
                        'val_acc': avg_val_acc,
                        'val_loss': avg_val_loss,
                    }, f'{CKPT_DIR}/keli_navy_best.pt')
                    print(f"  ** NEW BEST: {avg_val_acc*100:.2f}% **", flush=True)
                    # Resume training if we reach 90%
                    if avg_val_acc >= 0.90:
                        print(f"  ★ 90% TARGET REACHED at step {global_step}!", flush=True)
                else:
                    no_improve += 1
                    print(f"  No improve {no_improve}/10 (best: {best_val_acc*100:.2f}%)", flush=True)
                    if no_improve >= 10:
                        print(f"Early stopping at step {global_step}", flush=True)
                        torch.save({
                            'model_state': model.state_dict(),
                            'optimizer_state': optimizer.state_dict(),
                            'step': global_step,
                            'val_acc': avg_val_acc,
                            'val_loss': avg_val_loss,
                        }, f'{CKPT_DIR}/keli_navy_final.pt')
                        sys.exit(0)

                model.train()

                # Save latest checkpoint
                torch.save({
                    'model_state': model.state_dict(),
                    'optimizer_state': optimizer.state_dict(),
                    'step': global_step,
                    'val_acc': avg_val_acc,
                    'val_loss': avg_val_loss,
                    'best_val_acc': best_val_acc,
                }, f'{CKPT_DIR}/keli_navy_latest.pt')

    # End of epoch
    print(f"Epoch {epoch+1} complete. Step {global_step}", flush=True)
