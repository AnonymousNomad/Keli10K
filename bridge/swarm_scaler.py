"""
Swarm Scaler — replicates Keli10K's nanobot swarm from 10K → N without retraining.

Nanobot mitosis: each learned nanobot vector duplicates with tiny mutations,
preserving all learned capabilities while expanding coverage.

This works because:
  1. Nanobot embeddings are independent learned patterns [N, 200]
  2. Router weights map [dim] → [N] — each column = affinity for one bot
  3. Comm Gates average across all bots — naturally scale-invariant
  4. Territory biases per token — don't depend on N

So we tile every N-dependent tensor with small Gaussian noise.
"""
import torch
import torch.nn as nn
import math


def scale_swarm(model, target_bots, noise_std=0.015):
    """
    Scale Keli10K's nanobot swarm from current N to target_bots.
    Returns new Keli10K instance with expanded swarm.
    All weights preserved via tiling + noise.
    """
    old_n = model.n_nanobots
    if target_bots <= old_n:
        return model  # No scaling needed

    factor = target_bots // old_n
    remainder = target_bots % old_n
    if factor < 1:
        factor = 1
        remainder = 0

    actual_new = old_n * factor + remainder
    print(f"  Scaling swarm: {old_n:,} → {actual_new:,} nanobots (factor={factor}, rem={remainder})")

    _tile_embedding(model.nanobot_embed, factor, remainder, noise_std)
    _tile_linear_out(model.router[-1], factor, remainder, noise_std)

    if hasattr(model, 'task_router') and model.task_router is not None:
        _tile_task_router(model.task_router, factor, remainder, noise_std)

    model.n_nanobots = actual_new
    print(f"  Swarm scaled: {actual_new:,} bots, {model.count_parameters()/1e6:.2f}M params")
    return model


def _tile_embedding(embed, factor, remainder, noise_std):
    """Tile nn.Embedding weights: [N, D] → [N*factor+rem, D]"""
    old_weight = embed.weight.data
    D = old_weight.shape[1]

    tiles = [old_weight] * factor
    if remainder > 0:
        tiles.append(old_weight[:remainder])
    new_weight = torch.cat(tiles, dim=0)
    noise = torch.randn_like(new_weight) * noise_std
    new_weight = new_weight + noise

    new_embed = nn.Embedding(new_weight.shape[0], D)
    new_embed.weight.data = new_weight
    # Replace in module
    embed.weight = new_embed.weight
    embed.num_embeddings = new_weight.shape[0]


def _tile_linear_out(linear, factor, remainder, noise_std):
    """Tile linear output weights: [dim, N] → [dim, N*factor+rem]"""
    old_w = linear.weight.data  # [out, in] = [N, dim]
    old_b = linear.bias.data if linear.bias is not None else None

    tiles_w = [old_w] * factor
    if remainder > 0:
        tiles_w.append(old_w[:remainder])
    new_w = torch.cat(tiles_w, dim=0)
    new_w = new_w + torch.randn_like(new_w) * noise_std

    new_out = new_w.shape[0]
    new_linear = nn.Linear(linear.in_features, new_out, bias=old_b is not None)
    new_linear.weight.data = new_w

    if old_b is not None:
        tiles_b = [old_b] * factor
        if remainder > 0:
            tiles_b.append(old_b[:remainder])
        new_b = torch.cat(tiles_b, dim=0)
        new_b = new_b + torch.randn_like(new_b) * noise_std * 0.5
        new_linear.bias.data = new_b

    # Replace
    linear.weight = new_linear.weight
    linear.out_features = new_out
    if old_b is not None:
        linear.bias = new_linear.bias


def _tile_task_router(task_router, factor, remainder, noise_std):
    """Tile TaskRouter's final linear layer."""
    old_mlp = task_router.router_mlp[-1]
    old_w = old_mlp.weight.data
    old_b = old_mlp.bias.data if old_mlp.bias is not None else None

    tiles_w = [old_w] * factor
    if remainder > 0:
        tiles_w.append(old_w[:remainder])
    new_w = torch.cat(tiles_w, dim=0)
    new_w = new_w + torch.randn_like(new_w) * noise_std

    new_out = new_w.shape[0]
    new_linear = nn.Linear(old_mlp.in_features, new_out, bias=old_b is not None)
    new_linear.weight.data = new_w

    if old_b is not None:
        tiles_b = [old_b] * factor
        if remainder > 0:
            tiles_b.append(old_b[:remainder])
        new_b = torch.cat(tiles_b, dim=0)
        new_b = new_b + torch.randn_like(new_b) * noise_std * 0.5
        new_linear.bias.data = new_b

    task_router.router_mlp[-1] = new_linear
    task_router.n_bots = new_out


def compute_scale_factor(kimi_params_m):
    """
    Given Kimi-Vitalis parameter count in millions,
    compute target nanobot count to match model size.
    """
    keli_base = 25.1  # Base Keli10K params (millions)
    if kimi_params_m <= keli_base:
        return 10000

    ratio = kimi_params_m / keli_base
    target_bots = int(10000 * ratio)
    target_bots = max(10000, min(target_bots, 1_000_000))

    return target_bots


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/tmp/opencode/snca')
    from keli_10k import Keli10K
    from snca_config import SNCACfg

    cfg = SNCACfg()
    model = Keli10K(
        vocab_size=cfg.vocab_size, dim=cfg.d_model,
        n_heads=cfg.n_heads, n_layers=cfg.n_layers,
        ffn_hidden=cfg.d_ff, max_len=cfg.max_len,
        n_nanobots=10000, nanobot_dim=200,
        n_comm_rounds=5, dropout=cfg.dropout,
    )
    print(f"Before: {model.count_parameters()/1e6:.2f}M, bots={model.n_nanobots}")

    for target in [50000, 100000, 500000]:
        m2 = Keli10K(
            vocab_size=cfg.vocab_size, dim=cfg.d_model,
            n_heads=cfg.n_heads, n_layers=cfg.n_layers,
            ffn_hidden=cfg.d_ff, max_len=cfg.max_len,
            n_nanobots=10000, nanobot_dim=200,
            n_comm_rounds=5, dropout=cfg.dropout,
        )
        m2.load_state_dict(model.state_dict(), strict=False)
        scale_swarm(m2, target)
        print()
