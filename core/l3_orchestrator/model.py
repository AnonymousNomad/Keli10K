import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SparseAttention(nn.Module):
    def __init__(self, dim, n_heads, window=128):
        super().__init__()
        assert dim % n_heads == 0
        self.dim = dim
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.window = window
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out = nn.Linear(dim, dim, bias=False)

    def forward(self, x):
        B, T, D = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_heads, self.head_dim)
        q, k, v = qkv.unbind(2)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)

        local_mask = torch.zeros(T, T, device=x.device, dtype=torch.bool)
        for i in range(T):
            start = max(0, i - self.window)
            end = min(T, i + self.window + 1)
            local_mask[i, start:end] = True

        causal_mask = torch.tril(torch.ones(T, T, device=x.device, dtype=torch.bool))
        mask = local_mask & causal_mask

        attn_bias = torch.zeros(B, self.n_heads, T, T, device=x.device)
        attn_bias.masked_fill_(~mask.unsqueeze(0).unsqueeze(0), float('-inf'))

        attn = (q @ k.transpose(-2, -1)) * self.scale + attn_bias
        attn = F.softmax(attn, dim=-1)
        y = (attn @ v).transpose(1, 2).reshape(B, T, D)
        return self.out(y)


class OrchestratorBlock(nn.Module):
    def __init__(self, dim, n_heads, ffn_hidden, window=128, dropout=0.1):
        super().__init__()
        self.attn = SparseAttention(dim, n_heads, window)
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, ffn_hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(ffn_hidden, dim),
            nn.Dropout(dropout)
        )

    def forward(self, x):
        x = x + self.attn(self.norm1(x))
        x = x + self.ffn(self.norm2(x))
        return x


class OrchestratorModel(nn.Module):
    def __init__(self, vocab_size=8192, dim=512, n_layers=12, n_heads=8,
                 ffn_hidden=1536, max_seq_len=4096, window=128, dropout=0.1):
        super().__init__()
        self.dim = dim
        self.max_seq_len = max_seq_len

        self.embed = nn.Embedding(vocab_size, dim)
        self.pos = nn.Embedding(max_seq_len, dim)
        self.drop = nn.Dropout(dropout)

        self.blocks = nn.ModuleList([
            OrchestratorBlock(dim, n_heads, ffn_hidden, window, dropout)
            for _ in range(n_layers)
        ])

        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, vocab_size, bias=False)

        self.apply(self._init_weights)
        n = self._count_params()
        print(f"  OrchestratorModel: {n/1e6:.2f}M params")

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def _count_params(self):
        return sum(p.numel() for p in self.parameters())

    def forward(self, x):
        B, T = x.shape
        pos = torch.arange(0, T, device=x.device).unsqueeze(0)
        x = self.embed(x) + self.pos(pos)
        x = self.drop(x)
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        return self.head(x)

    def generate(self, idx, max_new=256, temperature=1.0, top_k=40):
        self.eval()
        with torch.no_grad():
            for _ in range(max_new):
                idx_cond = idx[:, -self.max_seq_len:]
                logits = self(idx_cond)
                logits = logits[:, -1, :] / temperature
                if top_k > 0:
                    v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                    logits[logits < v[:, [-1]]] = float('-inf')
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                idx = torch.cat((idx, next_token), dim=1)
                if next_token.item() == 3:
                    break
        return idx
