import sys, os, json, torch, time
sys.path.insert(0, '/tmp/opencode/snca')

from pathlib import Path
from torch.utils.data import IterableDataset
from snca_tokenizer import SNCATokenizer
from snca_config import SNCACfg
from keli_10k import Keli10K
import torch.nn.functional as F

cfg = SNCACfg()

ckpt_path = 'checkpoints/keli_navy_latest.pt'
n_bots = 100000
if os.path.exists(ckpt_path):
    try:
        tmp = torch.load(ckpt_path, map_location='cpu', weights_only=True)
        for k in tmp['model_state']:
            if 'nanobot_embed.weight' in k:
                n_bots = tmp['model_state'][k].shape[0]
                break
        del tmp
    except:
        pass

print(f"Using {n_bots:,} nanobots", flush=True)
model = Keli10K(
    vocab_size=cfg.vocab_size, dim=cfg.d_model,
    n_heads=cfg.n_heads, n_layers=cfg.n_layers,
    ffn_hidden=cfg.d_ff, max_len=cfg.max_len,
    n_nanobots=n_bots, nanobot_dim=200,
    n_comm_rounds=5, dropout=cfg.dropout,
)

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
PAD = 0
PRINT_EVERY = 10
BATCH_SIZE = 1
MAX_SEQ = 128

step = 0
best_loss = float('inf')

if os.path.exists(ckpt_path):
    try:
        ckpt = torch.load(ckpt_path, map_location='cpu')
        model.load_state_dict(ckpt['model_state'], strict=True)
        step = ckpt['step']
        best_loss = ckpt.get('best_loss', float('inf'))
        # Try loading optimizer, reset if shapes don't match
        try:
            optimizer.load_state_dict(ckpt['optimizer_state'])
            # Verify shapes
            for pg in optimizer.param_groups:
                for p in pg['params']:
                    if p in optimizer.state and 'exp_avg' in optimizer.state[p]:
                        if optimizer.state[p]['exp_avg'].shape != p.shape:
                            raise RuntimeError("Shape mismatch")
        except:
            print("Optimizer state reset (scaling detected)", flush=True)
            optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
        print(f"Resumed from step {step}", flush=True)
    except Exception as e:
        print(f"Checkpoint load failed ({e}), starting fresh", flush=True)

class FineDataset(IterableDataset):
    """High-quality curated subset from chunk files."""
    def __init__(self, chunk_dir, max_len=256, max_examples=50000):
        self.chunk_dir = Path(chunk_dir)
        self.max_len = max_len
        self.max_examples = max_examples
        self.chunk_files = sorted([f for f in self.chunk_dir.glob('*.jsonl') 
                                   if 'chunk_11' not in f.name and 'chunk_12' not in f.name])

    def __iter__(self):
        tok = SNCATokenizer()
        count = 0
        for file_path in self.chunk_files:
            with open(file_path) as f:
                for line in f:
                    if count >= self.max_examples: return
                    line = line.strip()
                    if not line: continue
                    try: item = json.loads(line)
                    except: continue
                    inp = item.get('input', '')
                    tgt = item.get('target', '')
                    if not inp or not tgt: continue
                    inp_ids = tok.encode(inp, bos=True, eos=False)
                    tgt_ids = tok.encode(tgt, bos=True, eos=True)
                    if not inp_ids or not tgt_ids: continue
                    ids = (inp_ids + tgt_ids)[:self.max_len]
                    mask = [0]*len(inp_ids) + [1]*len(tgt_ids)
                    mask = mask[:self.max_len]
                    count += 1
                    yield torch.tensor(ids, dtype=torch.long), torch.tensor(mask, dtype=torch.float)

dataset = FineDataset('data/chunks', max_len=MAX_SEQ, max_examples=50000)
model.train()
print(f"Training on curated set ({BATCH_SIZE}/batch, {MAX_SEQ} seq)", flush=True)

running_loss = 0
t0_total = time.time()

while True:
    try:
        dataset = FineDataset('data/chunks', max_len=MAX_SEQ, max_examples=50000)
    except:
        pass
    batch_ids, batch_masks = [], []
    for ids, mask in dataset:
        batch_ids.append(ids)
        batch_masks.append(mask)
        if len(batch_ids) >= BATCH_SIZE:
            ml = max(i.size(0) for i in batch_ids)
            pids = torch.full((len(batch_ids), ml), PAD, dtype=torch.long)
            pms = torch.zeros((len(batch_ids), ml), dtype=torch.float)
            for i, (id_, m) in enumerate(zip(batch_ids, batch_masks)):
                pids[i, :id_.size(0)] = id_
                pms[i, :m.size(0)] = m

            t0 = time.time()
            logits, _ = model(pids)
            loss = F.cross_entropy(logits.view(-1, cfg.vocab_size), pids.view(-1), reduction='none')
            loss = (loss * pms.view(-1)).sum() / pms.sum()
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            running_loss += loss.item()
            step += 1

            if step % PRINT_EVERY == 0:
                avg = running_loss / PRINT_EVERY
                elapsed = time.time() - t0_total
                speed = (time.time() - t0)
                print(f"[{elapsed/3600:.1f}h] step {step} loss {avg:.4f} ({speed:.1f}s/b)", flush=True)
                running_loss = 0

                os.makedirs('checkpoints', exist_ok=True)
                torch.save({
                    'model_state': model.state_dict(),
                    'optimizer_state': optimizer.state_dict(),
                    'step': step,
                    'best_loss': best_loss,
                }, 'checkpoints/keli_navy_latest.pt')

                if avg < best_loss:
                    best_loss = avg
                    torch.save({
                        'model_state': model.state_dict(),
                        'optimizer_state': optimizer.state_dict(),
                        'step': step,
                        'loss': best_loss,
                    }, 'checkpoints/keli_navy_best.pt')
                    print(f"  best: {best_loss:.4f}", flush=True)

            batch_ids, batch_masks = [], []
