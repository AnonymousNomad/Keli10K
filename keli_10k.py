import torch
import torch.nn as nn
import torch.nn.functional as F
import math

device = 'cuda' if torch.cuda.is_available() else 'cpu'

try:
    from orchestrator_boss import CoordinatorBots, TaskRouter, ParameterMonitor
    from orchestrator_boss import CoordinatorBots as BossOrchestrator
    HAVE_BOSS = True
except ImportError:
    HAVE_BOSS = False
    BossOrchestrator = None


class SparseAttention(nn.Module):
    def __init__(self, dim, n_heads, window=128, dropout=0.0):
        super().__init__()
        assert dim % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.scale = self.head_dim ** -0.5
        self.window = window
        self.qkv = nn.Linear(dim, dim * 3, bias=False)
        self.out = nn.Linear(dim, dim, bias=False)
        self.attn_drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x):
        B, T, D = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_heads, self.head_dim)
        q, k, v = qkv.unbind(2)
        q = q.transpose(1, 2)
        k = k.transpose(1, 2)
        v = v.transpose(1, 2)
        mask = self._sparse_causal_mask(T, x.device)
        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.masked_fill(mask == 0, float('-inf'))
        attn = F.softmax(attn, dim=-1)
        attn = self.attn_drop(attn)
        y = (attn @ v).transpose(1, 2).reshape(B, T, D)
        return self.out(y)

    def _sparse_causal_mask(self, T, dev):
        mask = torch.zeros(T, T, device=dev)
        # Global memory tokens: first 4 positions attend to all
        for i in range(min(4, T)):
            mask[i, :] = 1.0
        for i in range(4, T):
            start = max(0, i - self.window)
            end = min(T, i + self.window + 1)
            mask[i, start:end] = 1.0
        # All tokens attend to memory tokens
        mask[:, :min(4, T)] = 1.0
        causal = torch.tril(torch.ones(T, T, device=dev))
        mask = mask * causal
        return mask.unsqueeze(0).unsqueeze(0)


class TransformerBlock(nn.Module):
    def __init__(self, dim, n_heads, ffn_hidden, window=128, dropout=0.0):
        super().__init__()
        self.attn = SparseAttention(dim, n_heads, window, dropout)
        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)
        self.ffn = nn.Sequential(
            nn.Linear(dim, ffn_hidden),
            nn.GELU(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
            nn.Linear(ffn_hidden, dim),
        )
        self.drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x):
        x = x + self.drop(self.attn(self.norm1(x)))
        x = x + self.drop(self.ffn(self.norm2(x)))
        return x


class NanobotCommGate(nn.Module):
    def __init__(self, dim, dropout=0.0):
        super().__init__()
        self.gate = nn.Linear(dim, dim)
        self.drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

    def forward(self, x, nanobot_embs):
        B, T, D = x.shape
        gate_val = torch.sigmoid(self.gate(x.mean(dim=1, keepdim=True)))
        comm = nanobot_embs.mean(dim=0, keepdim=True).unsqueeze(0).expand(B, -1, -1)
        comm = F.adaptive_avg_pool1d(comm.transpose(1, 2), T).transpose(1, 2)
        return x + self.drop(gate_val * comm)


class Keli10K(nn.Module):
    TERRITORIES = ['frontend', 'backend', 'data', 'devops', 'auth']

    def __init__(self, vocab_size=8192, dim=384, n_heads=6, n_layers=7,
                 ffn_hidden=768, max_len=4096, window=128,
                 n_nanobots=10000, nanobot_dim=200, n_comm_rounds=5,
                 dropout=0.0):
        super().__init__()
        self.dim = dim
        self.max_len = max_len
        self.n_nanobots = n_nanobots
        self.nanobot_dim = nanobot_dim
        self.n_comm_rounds = n_comm_rounds

        self.embed = nn.Embedding(vocab_size, dim)
        self.pos = nn.Parameter(torch.zeros(1, max_len, dim))
        self.embed_drop = nn.Dropout(dropout) if dropout > 0 else nn.Identity()

        self.blocks = nn.ModuleList([
            TransformerBlock(dim, n_heads, ffn_hidden, window, dropout)
            for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(dim)

        self.nanobot_embed = nn.Embedding(n_nanobots, nanobot_dim)
        self.nanobot_proj = nn.Linear(nanobot_dim, dim)

        self.router = nn.Sequential(
            nn.Linear(dim, dim),
            nn.ReLU(),
            nn.Linear(dim, n_nanobots),
        )

        self.comm_gates = nn.ModuleList([
            NanobotCommGate(dim, dropout) for _ in range(n_comm_rounds)
        ])

        self.head = nn.Linear(dim, vocab_size, bias=False)
        self.embed.weight = self.head.weight
        self.head_drop = nn.Dropout(min(dropout, 0.05))

        self.territory_router = nn.Linear(dim, len(self.TERRITORIES))
        self.territory_bias = nn.Parameter(torch.zeros(len(self.TERRITORIES), vocab_size))

        if HAVE_BOSS:
            self.coordinators = CoordinatorBots(
                swarm_dim=dim, n_coords=10, coord_dim=64, n_bots=n_nanobots,
            )
            self.task_router = TaskRouter(n_bots=n_nanobots, swarm_dim=dim)

        self.mode_embed = nn.Embedding(2, dim)

        self.apply(self._init_weights)
        n = self.count_parameters()
        print(f"Keli10K initialized: {n/1e6:.2f}M parameters on {device} (dropout={dropout})")

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def count_parameters(self):
        return sum(p.numel() for p in self.parameters())

    def forward(self, input_ids, mode='plan', territory_idx=None):
        B, T = input_ids.shape
        pos = self.pos[:, :T, :]
        mode_id = 0 if mode == 'plan' else 1
        mode_emb = self.mode_embed(torch.tensor([mode_id], device=input_ids.device))
        x = self.embed(input_ids) + pos + mode_emb.unsqueeze(1)
        # First 4 positions are memory tokens (persistent state carriers)
        if T > 4:
            x[:, :4] = x[:, :4].detach() + 0.01 * x[:, :4] * torch.randn_like(x[:, :4])
        x = self.embed_drop(x)

        all_nanobot_embs = self.nanobot_proj(self.nanobot_embed.weight)

        for block in self.blocks:
            x = block(x)

        pooled = x.mean(dim=1)

        # Dynamic routing via Coordinators
        if HAVE_BOSS and hasattr(self, 'coordinators'):
            task_idx, task_probs, territory_weights, confidence = self.coordinators(pooled)
            router_probs = self.task_router(pooled, task_idx, territory_weights)
        else:
            router_logits = self.router(pooled)
            router_probs = F.softmax(router_logits, dim=-1)
            task_idx = torch.zeros(B, dtype=torch.long)
            territory_weights = torch.ones(B, len(self.TERRITORIES)) / len(self.TERRITORIES)
            confidence = torch.ones(B, 1)

        # Activate bots proportional to territory weights
        if mode == 'build':
            min_active = max(1, self.n_nanobots // 32)
            max_active = self.n_nanobots
            active_pct = 0.25 + 0.75 * (1 - confidence).mean()
            top_k = int(min_active + active_pct * (max_active - min_active))
        else:
            top_k = min(self.n_nanobots, max(1, self.n_nanobots // 16))

        topk_vals, topk_idx = torch.topk(router_probs, top_k, dim=-1)

        selected_embs = F.embedding(topk_idx, all_nanobot_embs)
        weights = F.softmax(topk_vals / 0.1, dim=-1)
        weighted = (selected_embs * weights.unsqueeze(-1)).sum(dim=1)
        x = x + weighted.unsqueeze(1).expand(-1, T, -1)

        for gate in self.comm_gates:
            x = gate(x, all_nanobot_embs)

        x = self.norm(x)

        logits = self.head(self.head_drop(x))

        if mode == 'build':
            for b_idx in range(B):
                tw = territory_weights[b_idx]
                for t_idx in range(min(len(self.TERRITORIES), tw.size(0))):
                    logits[b_idx] = logits[b_idx] + self.territory_bias[t_idx] * tw[t_idx]

        if HAVE_BOSS and hasattr(self, 'coordinators'):
            return logits, router_probs
        return logits, locals().get('router_logits', torch.zeros(B, self.n_nanobots))

    def generate(self, input_ids, max_new=256, temperature=0.7, top_k=40,
                 mode='plan', territory_idx=None):
        self.eval()
        with torch.no_grad():
            for _ in range(max_new):
                if input_ids.size(1) > self.max_len:
                    input_ids = input_ids[:, -self.max_len:]
                logits, _ = self(input_ids, mode=mode, territory_idx=territory_idx)
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


class Keli10KModel:
    def __init__(self, cfg):
        self.device = device
        self.model = Keli10K(
            vocab_size=cfg.vocab_size,
            dim=cfg.d_model,
            n_heads=cfg.n_heads,
            n_layers=8,
            ffn_hidden=cfg.d_ff,
            max_len=cfg.max_len,
            window=cfg.local_window,
            dropout=cfg.dropout,
        ).to(device)
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=1e-4, betas=(0.9, 0.95), weight_decay=0.01
        )
        n = self.model.count_parameters()
        if HAVE_BOSS and hasattr(self.model, 'coordinators'):
            n += sum(p.numel() for p in self.model.coordinators.parameters())
            n += sum(p.numel() for p in self.model.task_router.parameters())
        print(f"Keli10KModel total: {n/1e6:.2f}M")
        self.monitor = ParameterMonitor(self) if HAVE_BOSS else None

    def get_utilization(self):
        if self.monitor:
            return self.monitor.get_utilization()
        return {}

    def save(self, path):
        torch.save({
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict(),
        }, path)

    def load(self, path):
        ckpt = torch.load(path, map_location=self.device)
        if isinstance(ckpt, dict) and 'model_state' in ckpt:
            self.model.load_state_dict(ckpt['model_state'], strict=False)
            if 'optimizer_state' in ckpt and ckpt['optimizer_state'] and 'param_groups' in ckpt['optimizer_state']:
                self.optimizer.load_state_dict(ckpt['optimizer_state'])
        else:
            self.model.load_state_dict(ckpt)

    def generate(self, input_ids, max_new=256, temperature=0.7, top_k=40,
                 mode='plan', territory_idx=None):
        return self.model.generate(
            input_ids, max_new=max_new, temperature=temperature,
            top_k=top_k, mode=mode, territory_idx=territory_idx
        )


if __name__ == '__main__':
    from snca_config import SNCACfg
    cfg = SNCACfg()
    model = Keli10KModel(cfg)
    n = model.model.count_parameters()
    print(f"Keli10K parameter count: {n/1e6:.2f}M")
    assert 20e6 <= n <= 23e6, f"FAIL: {n/1e6:.2f}M outside 20-23M range"
    print(f"Target was 21.4M, got {n/1e6:.2f}M")
    print(f"Parameter count PASS: {n/1e6:.2f}M")
