import sys, os, json, math, time, torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
torch.set_num_threads(2)

PAD = 0

class LazyDataset(Dataset):
    def __init__(self, data, max_len=1024):
        self.data = data; self.max_len = max_len
        self.valid = [i for i, item in enumerate(data) if item.get('input_ids') and item.get('target_ids')]
    def __len__(self): return len(self.valid)
    def __getitem__(self, idx):
        item = self.data[self.valid[idx]]
        ids = (item['input_ids'] + item['target_ids'])[:self.max_len]
        mask = [0]*len(item['input_ids']) + [1]*len(item['target_ids'])
        return {'input_ids': torch.tensor(ids[:self.max_len], dtype=torch.long),
                'mask': torch.tensor(mask[:self.max_len], dtype=torch.float),
                'mode': item.get('mode','plan'), 'domain': item.get('domain','unknown')}

def collate(batch):
    ids = [b['input_ids'] for b in batch]
    masks = [b['mask'] for b in batch]
    max_len = max(len(i) for i in ids)
    pad_ids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    pad_masks = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (id_, m) in enumerate(zip(ids, masks)):
        pad_ids[i, :len(id_)] = id_
        pad_masks[i, :len(m)] = torch.as_tensor(m, dtype=torch.float)
    return pad_ids, pad_masks, [b['mode'] for b in batch], [b['domain'] for b in batch]

def loss_acc(logits, targets, mask):
    sl = logits[:, :-1, :].contiguous()
    st = targets[:, 1:].contiguous()
    sm = mask[:, 1:].contiguous()
    loss = F.cross_entropy(sl.view(-1, sl.size(-1)), st.view(-1), reduction='none')
    loss = loss.view(sl.size(0), -1)
    ml = (loss * sm).sum() / (sm.sum() + 1e-8)
    corr = ((sl.argmax(dim=-1) == st) * sm.bool()).sum().float()
    acc = corr / (sm.sum() + 1e-8)
    return ml, acc

from snca_config import SNCACfg
from keli_10k import Keli10KModel

cfg = SNCACfg()
model = Keli10KModel(cfg)
print(f'Model: {sum(p.numel() for p in model.model.parameters())/1e6:.2f}M')

with open('data/combined/train.jsonl') as f: train_data = [json.loads(l) for l in f]
with open('data/combined/val.jsonl') as f: val_data = [json.loads(l) for l in f]
print(f'Train: {len(train_data)} | Val: {len(val_data)}')

train_loader = DataLoader(LazyDataset(train_data), batch_size=4, shuffle=True, collate_fn=collate)
val_loader = DataLoader(LazyDataset(val_data), batch_size=4, shuffle=False, collate_fn=collate)
opt = torch.optim.AdamW(model.model.parameters(), lr=5e-4, weight_decay=0.01, betas=(0.9, 0.95))

total_steps = len(train_loader)  # 1 epoch, accum=2
warmup = min(500, total_steps // 10)
print(f'Steps: ~{total_steps}, warmup: {warmup}')

def lr_fn(s):
    if s < warmup: return 5e-4 * (s + 1) / (warmup + 1)
    prog = (s - warmup) / max(total_steps - warmup, 1)
    return 5e-4 * 0.5 * (1.0 + math.cos(math.pi * prog))

step = 0; best_val = 0.0; no_impr = 0
for epoch in range(2):
    model.model.train()
    accum_loss = 0.0; accum_acc = 0.0; accum_n = 0
    ep_start = time.time()
    for bidx, (ids, mask, modes, domains) in enumerate(train_loader):
        lr = lr_fn(step)
        for pg in opt.param_groups: pg['lr'] = lr
        targets = ids.clone(); targets[targets == PAD] = -100
        logits, _ = model.model(ids, mode='build' if all(m == 'build' for m in modes) else 'plan')
        loss, acc = loss_acc(logits, targets, mask)
        (loss / 2).backward()
        accum_loss += loss.item(); accum_acc += acc.item(); accum_n += 1
        if (bidx + 1) % 2 == 0:
            torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
            opt.step(); opt.zero_grad()
            sl = accum_loss / accum_n; sa = accum_acc / accum_n
            accum_loss = 0.0; accum_acc = 0.0; accum_n = 0; step += 1
            if step % 100 == 0:
                ppl = math.exp(min(sl, 20))
                print(f'Step {step:5d} | loss={sl:.4f} acc={sa:.4f} ppl={ppl:.2f} lr={lr:.2e} ({time.time()-ep_start:.1f}s)')
                ep_start = time.time()
            if step % 500 == 0:
                model.model.eval()
                vl = 0.0; va = 0.0; nv = 0
                print(f'  Validating ({len(val_loader)} batches)...')
                with torch.no_grad():
                    for vids, vmask, vmodes, _ in val_loader:
                        vtargs = vids.clone(); vtargs[vtargs == PAD] = -100
                        vlogits, _ = model.model(vids, mode='build' if all(m == 'build' for m in vmodes) else 'plan')
                        vl_i, va_i = loss_acc(vlogits, vtargs, vmask)
                        vl += vl_i.item(); va += va_i.item(); nv += 1
                model.model.train()
                avg_vl = vl / max(nv, 1); avg_va = va / max(nv, 1)
                vppl = math.exp(min(avg_vl, 20))
                s = f'val_loss={avg_vl:.4f} val_acc={avg_va:.4f} val_ppl={vppl:.2f}'
                if avg_va > best_val:
                    best_val = avg_va; no_impr = 0
                    torch.save({'model_state': model.model.state_dict(), 'optimizer_state': opt.state_dict()}, 'checkpoints/keli_best.pt')
                    print(f'  ** {s} ** NEW BEST')
                else:
                    no_impr += 1
                    print(f'  {s} (no improve {no_impr}/5)')
                    if no_impr >= 5:
                        print(f'Early stop at step {step}')
                        torch.save({'model_state': model.model.state_dict(), 'optimizer_state': opt.state_dict()}, 'checkpoints/keli_final.pt')
                        exit()

torch.save({'model_state': model.model.state_dict(), 'optimizer_state': opt.state_dict()}, 'checkpoints/keli_final.pt')
print(f'Done. Best val_acc: {best_val:.4f}')
