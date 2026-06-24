import torch
import torch.nn as nn
import torch.nn.functional as F
import math

device = 'cuda' if torch.cuda.is_available() else 'cpu'

class SparseAttention(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.n_heads = cfg.n_heads
        self.head_dim = cfg.d_model // cfg.n_heads
        self.scale = self.head_dim ** -0.5
        self.local_window = cfg.local_window
        self.qkv = nn.Linear(cfg.d_model, cfg.d_model * 3, bias=False)
        self.out = nn.Linear(cfg.d_model, cfg.d_model, bias=False)

    def forward(self, x, mask=None):
        B, T, D = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_heads, self.head_dim)
        q, k, v = qkv.unbind(2)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        if mask is None:
            mask = self._create_sparse_mask(T, x.device)

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.masked_fill(mask == 0, float('-inf'))
        attn = F.softmax(attn, dim=-1)
        y = (attn @ v).transpose(1, 2).reshape(B, T, D)
        return self.out(y)

    def _create_sparse_mask(self, seq_len, device):
        w = self.local_window
        mask = torch.zeros(seq_len, seq_len, device=device)
        for i in range(seq_len):
            start = max(0, i - w)
            end = min(seq_len, i + w + 1)
            mask[i, start:end] = 1.0
        causal = torch.tril(torch.ones(seq_len, seq_len, device=device))
        mask = mask * causal
        mask = mask.unsqueeze(0).unsqueeze(0)
        return mask


class TransformerLayer(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.attn = SparseAttention(cfg)
        self.norm1 = nn.LayerNorm(cfg.d_model)
        self.ffn = nn.Sequential(
            nn.Linear(cfg.d_model, cfg.d_ff),
            nn.GELU(),
            nn.Linear(cfg.d_ff, cfg.d_model),
        )
        self.norm2 = nn.LayerNorm(cfg.d_model)

    def forward(self, x, mask=None):
        x = x + self.attn(self.norm1(x), mask)
        x = x + self.ffn(self.norm2(x))
        return x


class SNCAOrchestrator(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.embed = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.pos = nn.Parameter(torch.zeros(1, cfg.max_len, cfg.d_model))
        self.layers = nn.ModuleList([
            TransformerLayer(cfg) for _ in range(cfg.n_layers)
        ])
        self.norm = nn.LayerNorm(cfg.d_model)
        self.head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.apply(self._init_weights)
        n = self.count_parameters()
        assert 18e6 <= n <= 23e6, f"Parameter count {n/1e6:.2f}M outside target 18-23M"

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def count_parameters(self):
        return sum(p.numel() for p in self.parameters())

    def forward(self, input_ids):
        B, T = input_ids.shape
        pos = self.pos[:, :T, :]
        x = self.embed(input_ids) + pos
        for layer in self.layers:
            x = layer(x)
        x = self.norm(x)
        return self.head(x)


class SNCAModel:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model = SNCAOrchestrator(cfg).to(device)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=1e-4, betas=(0.9, 0.95))
        self.device = device
        n = self.model.count_parameters()
        print(f"SNCAModel initialized: {n/1e6:.2f}M parameters on {device}")

    def save(self, path):
        torch.save({
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
            'cfg': self.cfg,
        }, path)

    def load(self, path):
        ckpt = torch.load(path, map_location=self.device)
        self.model.load_state_dict(ckpt['model_state'])
        self.optimizer.load_state_dict(ckpt['optimizer_state'])
        print(f"Loaded checkpoint from {path}")

    def generate(self, input_ids, max_new=512, temperature=0.7, top_k=40):
        self.model.eval()
        with torch.no_grad():
            for _ in range(max_new):
                if input_ids.size(1) > self.cfg.max_len:
                    input_ids = input_ids[:, -self.cfg.max_len:]
                logits = self.model(input_ids)
                logits = logits[:, -1, :] / temperature
                if top_k > 0:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = float('-inf')
                probs = F.softmax(logits, dim=-1)
                next_id = torch.multinomial(probs, num_samples=1)
                input_ids = torch.cat((input_ids, next_id), dim=1)
                if next_id.item() == 1:
                    break
        return input_ids


if __name__ == '__main__':
    from snca_config import SNCACfg
    cfg = SNCACfg()
    model = SNCAModel(cfg)
    n = model.model.count_parameters()
    print(f"Parameter count: {n/1e6:.2f}M")
    assert 18e6 <= n <= 22e6, f"FAIL: {n/1e6:.2f}M outside 18-22M range"
    print(f"Parameter count PASS: {n/1e6:.2f}M")
