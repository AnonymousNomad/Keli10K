"""10 coordinator bots: task classifier + dynamic swarm partitioner."""
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class CoordinatorBots(nn.Module):
    """10 coordinators that classify task type and partition the 10K swarm."""

    N_TERRITORIES = 5  # HTML, CSS, JS, Python, DB
    TASK_TYPES = ['engineering', 'creative', 'debug', 'chat']

    def __init__(self, swarm_dim=384, n_coords=10, coord_dim=64, n_bots=10000):
        super().__init__()
        self.n_coords = n_coords
        self.coord_dim = coord_dim
        self.n_bots = n_bots

        self.coord_states = nn.Parameter(torch.randn(n_coords, coord_dim) * 0.02)
        self.query_proj = nn.Linear(swarm_dim, coord_dim)

        self.task_classifier = nn.Sequential(
            nn.Linear(coord_dim, 32),
            nn.GELU(),
            nn.Linear(32, len(self.TASK_TYPES)),
        )

        # Territory allocator per task type
        self.territory_allocator = nn.ModuleDict({
            task: nn.Linear(coord_dim, self.N_TERRITORIES)
            for task in self.TASK_TYPES
        })

        self.confidence_gate = nn.Sequential(
            nn.Linear(coord_dim, 16),
            nn.GELU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def forward(self, pooled):
        B = pooled.size(0)
        coord_embs = self.coord_states.unsqueeze(0).expand(B, -1, -1)

        c = coord_embs + self.query_proj(pooled).unsqueeze(1)
        c_agg = c.mean(dim=1)

        task_logits = self.task_classifier(c_agg)
        task_probs = F.softmax(task_logits, dim=-1)
        task_idx = task_probs.argmax(dim=-1)

        raw_territory = torch.zeros(B, self.N_TERRITORIES)
        for b in range(B):
            t = self.TASK_TYPES[task_idx[b].item()]
            raw_territory[b] = self.territory_allocator[t](c_agg[b])

        territory_weights = F.softmax(raw_territory, dim=-1)

        # Confidence = collective agreement (lower entropy = higher confidence)
        entropy = -(task_probs * torch.log(task_probs + 1e-8)).sum(dim=-1)
        confidence = 1.0 - (entropy / math.log(len(self.TASK_TYPES)))
        confidence = confidence.unsqueeze(-1)

        return task_idx, task_probs, territory_weights, confidence


class TaskRouter(nn.Module):
    """Routes the 10K swarm based on task type from coordinators."""

    def __init__(self, n_bots=10000, swarm_dim=384):
        super().__init__()
        self.n_bots = n_bots
        self.task_embed = nn.Embedding(len(CoordinatorBots.TASK_TYPES), swarm_dim)
        self.router_mlp = nn.Sequential(
            nn.Linear(swarm_dim, swarm_dim // 2),
            nn.GELU(),
            nn.Linear(swarm_dim // 2, n_bots),
        )

    def forward(self, pooled, task_idx, territory_weights):
        B = pooled.size(0)
        task_emb = self.task_embed(task_idx)
        route_input = pooled + task_emb

        router_logits = self.router_mlp(route_input)
        router_probs = F.softmax(router_logits, dim=-1)

        # Apply territory weights to bias bot selection (non-inplace)
        weight_factor = 1.0 + territory_weights.sum(dim=-1, keepdim=True)
        router_probs = router_probs * weight_factor

        router_probs = router_probs / router_probs.sum(dim=-1, keepdim=True)
        return router_probs


class ParameterMonitor:
    """Track utilization, territory load, active bots."""

    def __init__(self, model):
        self.model = model

    def get_utilization(self, pooled=None):
        import math as _m
        stats = {}
        m = self.model.model if hasattr(self.model, 'model') else self.model
        n_bots = getattr(m, 'n_nanobots', 10000)

        if hasattr(m, 'router'):
            with torch.no_grad():
                dummy = torch.zeros(1, 384)
                router_out = m.router(dummy)
                router_probs = F.softmax(router_out, dim=-1)
                active = (router_probs > (1.0 / n_bots)).float().sum().item()
                stats['active_bots'] = active
                stats['total_bots'] = n_bots
                stats['bot_utilization_pct'] = (active / n_bots) * 100

        alive = 0
        total = 0
        for p in m.parameters():
            alive += (torch.abs(p.data) > 0.001).sum().item()
            total += p.numel()
        stats['alive_weights'] = alive
        stats['total_weights'] = total
        stats['weight_utilization_pct'] = (alive / max(total, 1)) * 100

        if hasattr(m, 'comm_gates'):
            stats['communication_rounds'] = len(m.comm_gates)
            stats['communication_density'] = float(getattr(m, 'n_comm_rounds', 7))

        return stats

    def format_hud(self, stats):
        bots = f"{stats.get('active_bots', 0):.0f}/{stats.get('total_bots', 10000):,}"
        w = f"{stats.get('weight_utilization_pct', 0):.0f}%"
        return f"Bots: {bots} active | Weights: {w} utilized"
