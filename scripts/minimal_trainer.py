import sys, os, json, torch, time
sys.path.insert(0, '/tmp/opencode/snca')

from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from snca_tokenizer import SNCATokenizer
from snca_config import SNCACfg
from keli_10k import Keli10K
import torch.nn.functional as F

cfg = SNCACfg()
model = Keli10K(
    vocab_size=cfg.vocab_size,
    dim=cfg.d_model,
    n_heads=cfg.n_heads,
    n_layers=cfg.n_layers,
    ffn_hidden=cfg.d_ff,
    max_len=cfg.max_len,
    n_nanobots=10000,
    nanobot_dim=200,
    n_comm_rounds=5,
    dropout=cfg.dropout,
)

ckpt_path = 'checkpoints/keli_best.pt'
if os.path.exists(ckpt_path):
    try:
        ckpt = torch.load(ckpt_path, map_location='cpu')
        if 'model_state' in ckpt:
            model.load_state_dict(ckpt['model_state'], strict=False)
            print(f"Loaded checkpoint from {ckpt_path}")
        else:
            model.load_state_dict(ckpt, strict=False)
            print(f"Loaded raw checkpoint from {ckpt_path}")
    except Exception as e:
        print(f"Checkpoint load failed: {e}. Starting from random init.")
else:
    print("No checkpoint found. Starting from random init.")

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
PAD = 0

class SimpleDataset(Dataset):
    def __init__(self, path, max_len=384, max_items=10000):
        self.max_len = max_len
        self.items = []
        tok = SNCATokenizer()
        with open(path) as f:
            for i, line in enumerate(f):
                if len(self.items) >= max_items:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except:
                    continue
                inp = item.get('input', '')
                tgt = item.get('target', '')
                if not inp or not tgt:
                    continue
                input_ids = tok.encode(inp, bos=True, eos=False)
                target_ids = tok.encode(tgt, bos=True, eos=True)
                if not input_ids or not target_ids:
                    continue
                ids = (input_ids + target_ids)[:max_len]
                mask = [0] * len(input_ids) + [1] * len(target_ids)
                mask = mask[:max_len]
                self.items.append({
                    'ids': torch.tensor(ids, dtype=torch.long),
                    'mask': torch.tensor(mask, dtype=torch.float),
                })
        print(f"Loaded {len(self.items)} examples from {path}")

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]['ids'], self.items[idx]['mask']

def collate(batch):
    ids_list, masks_list = zip(*batch)
    max_len = max(len(i) for i in ids_list)
    pids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    pms = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (ids, mask) in enumerate(zip(ids_list, masks_list)):
        pids[i, :len(ids)] = ids
        pms[i, :len(mask)] = mask
    return pids, pms

# Find training data (chunk format with input/target text fields)
data_path = 'data/chunks/chunk_01.jsonl'
if not os.path.exists(data_path):
    data_files = list(Path('data').rglob('*.jsonl'))
    data_path = str(data_files[0]) if data_files else None
print(f"Using: {data_path}")

dataset = SimpleDataset(data_path, max_len=384, max_items=5000)
loader = DataLoader(dataset, batch_size=4, shuffle=True, collate_fn=collate, drop_last=True)

print(f"Starting training: {len(dataset)} examples, batch_size=4")
model.train()

step = 0
for epoch in range(3):
    epoch_loss = 0
    for batch_idx, (ids, mask) in enumerate(loader):
        t0 = time.time()
        logits, _ = model(ids)
        logits_flat = logits.view(-1, cfg.vocab_size)
        targets_flat = ids.view(-1)
        mask_flat = mask.view(-1)
        loss = F.cross_entropy(logits_flat, targets_flat, reduction='none')
        loss = (loss * mask_flat).sum() / mask_flat.sum()
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        epoch_loss += loss.item()
        step += 1
        if step % 5 == 0:
            print(f"Step {step} | Loss: {loss.item():.4f} | Time: {time.time()-t0:.1f}s")
        if step >= 1000:
            break
    avg_loss = epoch_loss / max(len(loader), 1)
    print(f"Epoch {epoch+1} complete. Avg loss: {avg_loss:.4f}")
    os.makedirs('checkpoints', exist_ok=True)
    torch.save({
        'model_state': model.state_dict(),
        'optimizer_state': optimizer.state_dict(),
        'step': step,
        'epoch': epoch,
    }, f'checkpoints/keli_minimal_step{step}.pt')
    print(f"Saved: checkpoints/keli_minimal_step{step}.pt")

print("Training complete.")
