#!/usr/bin/env python3
"""Train Boss orchestrator on multi-territory routing tasks."""
import sys, os, json, math, time, random, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from pathlib import Path

from snca_config import SNCACfg
from keli_10k import Keli10KModel

torch.set_num_threads(4)
device = 'cpu'
BATCH_SIZE = 8
LR = 1e-4
EPOCHS_PHASE1 = 3
EPOCHS_PHASE2 = 2

# ─── Multi-Territory Training Data ───────────────────────────────────────
# Each example: input_text → territory_mask [frontend, backend, data, devops, confidence]

TERRITORY_EXAMPLES = [
    # Full-stack multi-territory
    ("Build a React frontend with FastAPI backend and SQLite database", [1,1,1,0,0]),
    ("Create a full-stack todo app with React, Node.js, and PostgreSQL", [1,1,1,0,0]),
    ("Build a web app with HTML, CSS, and a Python server", [1,0,1,0,0]),
    ("Deploy a Docker container with Redis and PostgreSQL", [0,0,1,1,0]),
    ("Build a chat app with React frontend, WebSocket backend, and MongoDB", [1,1,1,0,0]),
    ("Create a login system with React form, JWT auth, and user database", [1,1,1,0,1]),
    # Frontend only
    ("Build an HTML button with hover effects", [1,0,0,0,0]),
    ("Create a responsive navigation bar with CSS Flexbox", [1,0,0,0,0]),
    ("Build a React counter component", [1,0,0,0,0]),
    ("Style a modal dialog with CSS animations", [1,0,0,0,0]),
    ("Create a CSS grid layout for a dashboard", [1,0,0,0,0]),
    # Backend only
    ("Write a Python FastAPI endpoint that returns JSON", [0,0,1,0,0]),
    ("Create a SQL query to join users and orders tables", [0,0,1,0,0]),
    ("Build an Express.js REST API with CRUD operations", [0,0,1,0,0]),
    ("Write a Python function to read a CSV file", [0,0,1,0,0]),
    ("Create a database schema for an e-commerce site", [0,0,1,0,0]),
    # Devops
    ("Write a Dockerfile for a Node.js application", [0,0,0,1,0]),
    ("Create a Kubernetes deployment YAML", [0,0,0,1,0]),
    ("Set up a CI/CD pipeline with GitHub Actions", [0,0,0,1,0]),
    ("Configure Nginx as a reverse proxy", [0,0,0,1,0]),
    # Auth
    ("Add user authentication with JWT tokens", [0,0,0,0,1]),
    ("Set up OAuth2 login with Google provider", [0,0,0,0,1]),
    ("Create a session-based login system with cookies", [0,0,0,0,1]),
    ("Implement role-based access control middleware", [0,0,0,0,1]),
    ("Write a password hashing and verification utility", [0,0,0,0,1]),
    # Mixed with auth
    ("Build a React form that POSTs to a FastAPI endpoint", [1,0,1,0,0]),
    ("Create a dashboard that fetches data from a SQL database", [1,0,1,0,0]),
    ("Deploy a Django app with PostgreSQL on AWS", [0,0,1,1,0]),
    ("Build a real-time dashboard with React, WebSocket, and InfluxDB", [1,1,1,0,0]),
    ("Containerize a full-stack app with Docker Compose", [1,1,1,1,0]),
    ("Build a login page with React, JWT auth, and user database", [1,1,1,0,1]),
    ("Create a secure API with Express, JWT, and rate limiting", [0,0,1,0,1]),
]


class TerritoryDataset(Dataset):
    def __init__(self, examples, augment=True):
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from snca_tokenizer import SNCATokenizer
        self.tok = SNCATokenizer()
        self.examples = []
        for text, mask in examples:
            ids = self.tok.encode(text)
            self.examples.append((ids, torch.tensor(mask, dtype=torch.float)))
        if augment:
            for _ in range(5):
                for text, mask in examples:
                    prefix = random.choice(['Build ', 'Create ', 'Write ', 'Make ', 'Develop '])
                    new_text = prefix + text.split(' ', 1)[-1] if ' ' in text else text
                    ids = self.tok.encode(new_text)
                    self.examples.append((ids, torch.tensor(mask, dtype=torch.float)))
        print(f'TerritoryDataset: {len(self.examples)} examples')

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        ids, mask = self.examples[idx]
        return torch.tensor(ids[:256], dtype=torch.long), mask


def collate_fn(batch):
    ids = [b[0] for b in batch]
    masks = torch.stack([b[1] for b in batch])
    max_len = max(len(i) for i in ids)
    pids = torch.zeros((len(batch), max_len), dtype=torch.long)
    for i, id_ in enumerate(ids):
        pids[i, :len(id_)] = id_
    return pids, masks


# ─── Training ────────────────────────────────────────────────────────────

def train_phase1(model, dataset, save_path='checkpoints/keli_v2_boss.pt'):
    """Phase 1: Freeze 10K swarm, train only Boss."""
    print(f'\n=== PHASE 1: Train Boss (frozen swarm) ===')

    # Freeze all 10K parameters
    for name, p in model.model.named_parameters():
        if 'boss' not in name and 'multi_territory' not in name:
            p.requires_grad = False

    trainable = sum(p.numel() for p in model.model.parameters() if p.requires_grad)
    print(f'Trainable params: {trainable:,}')

    optimizer = torch.optim.AdamW(
        [p for p in model.model.parameters() if p.requires_grad],
        lr=LR, weight_decay=0.01
    )

    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)

    for epoch in range(EPOCHS_PHASE1):
        total_loss = 0.0
        n = 0
        t0 = time.time()

        for batch_idx, (input_ids, target_masks) in enumerate(loader):
            optimizer.zero_grad()

            pooled = model.model.embed(input_ids).mean(dim=1)
            boss_mask, confidence = model.model.boss(pooled, mode='build')

            loss = F.binary_cross_entropy(boss_mask, target_masks, reduction='mean')
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            n += 1

            if batch_idx % 10 == 0:
                acc = ((boss_mask > 0.5).float() == target_masks).float().mean().item()
                print(f'  E{epoch+1} B{batch_idx}: loss={loss.item():.4f} acc={acc:.4f}')

        avg = total_loss / max(n, 1)
        elapsed = time.time() - t0
        print(f'  Epoch {epoch+1}: avg_loss={avg:.4f} ({elapsed:.1f}s)')

    # Save
    model.save(save_path)
    print(f'Saved to {save_path}')

    # Unfreeze all for Phase 2
    for p in model.model.parameters():
        p.requires_grad = True

    return model


def train_phase2(model, dataset, save_path='checkpoints/keli_v2_boss.pt'):
    """Phase 2: Joint train on multi-territory examples."""
    print(f'\n=== PHASE 2: Joint training ===')

    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    optimizer = torch.optim.AdamW(model.model.parameters(), lr=LR * 0.1, weight_decay=0.01)

    for epoch in range(EPOCHS_PHASE2):
        total_loss = 0.0
        n = 0
        t0 = time.time()

        for batch_idx, (input_ids, target_masks) in enumerate(loader):
            optimizer.zero_grad()

            pooled = model.model.embed(input_ids).mean(dim=1)
            boss_mask, confidence = model.model.boss(pooled, mode='build')

            loss = F.binary_cross_entropy(boss_mask, target_masks, reduction='mean')

            # Bonus: reward when all requested territories activate
            bonus = 0.1 * (boss_mask * target_masks).sum(dim=-1).mean()
            total = loss - bonus

            total.backward()
            optimizer.step()

            total_loss += loss.item()
            n += 1

            if batch_idx % 10 == 0:
                acc = ((boss_mask > 0.5).float() == target_masks).float().mean().item()
                print(f'  E{epoch+1} B{batch_idx}: loss={loss.item():.4f} acc={acc:.4f} bonus={bonus.item():.4f}')

        avg = total_loss / max(n, 1)
        elapsed = time.time() - t0
        print(f'  Epoch {epoch+1}: avg_loss={avg:.4f} ({elapsed:.1f}s)')

    model.save(save_path)
    print(f'Saved to {save_path}')
    return model


# ─── Test ────────────────────────────────────────────────────────────────

def test_boss(model):
    """Test Boss territory routing on example queries."""
    from snca_tokenizer import SNCATokenizer
    tok = SNCATokenizer()

    print(f'\n=== BOSS ROUTING TEST ===')
    tests = [
        "Build a React button with hover",
        "Create a FastAPI endpoint with database",
        "Deploy Docker on Kubernetes",
        "Build a full-stack app with React, FastAPI, SQLite",
        "Write a Python function",
        "Build a React form with Node.js backend and MongoDB",
    ]

    territory_names = ['frontend', 'backend', 'data', 'devops', 'auth']

    model.model.eval()
    for test in tests:
        ids = tok.encode(test)[:256]
        x = torch.tensor([ids], dtype=torch.long)
        with torch.no_grad():
            pooled = model.model.embed(x).mean(dim=1)
            mask, confidence = model.model.boss(pooled, mode='build')

        active = [f'{territory_names[i]}={mask[0,i].item():.2f}'
                  for i in range(5) if mask[0,i] > 0.3]
        print(f'  Input: {test[:50]}...')
        print(f'    Territories: {active} (conf={confidence.item():.2f})')


if __name__ == '__main__':
    cfg = SNCACfg()
    model = Keli10KModel(cfg)

    # Load base checkpoint
    ckpt_path = 'checkpoints/keli_best.pt'
    if os.path.exists(ckpt_path):
        model.load(ckpt_path)
        print(f'Loaded base from {ckpt_path}')

    # Check if boss already trained
    boss_path = 'checkpoints/keli_v2_boss.pt'
    if os.path.exists(boss_path):
        model.load(boss_path)
        print(f'Loaded Boss from {boss_path}')
        test_boss(model)
    else:
        dataset = TerritoryDataset(TERRITORY_EXAMPLES)
        model = train_phase1(model, dataset, boss_path)
        model = train_phase2(model, dataset, boss_path)
        test_boss(model)
