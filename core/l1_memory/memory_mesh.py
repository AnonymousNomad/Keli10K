import numpy as np
import time
import json
from pathlib import Path
from typing import List, Optional

class Hippocampus:
    def __init__(self, dim=128, max_episodes=100000, decay_rate=0.95, decay_unit_hours=24):
        self.dim = dim
        self.max_episodes = max_episodes
        self.decay_rate = decay_rate
        self.decay_unit_hours = decay_unit_hours
        self.episodes = []
        self.index = []

    def add_episode(self, query_embed, snippets, bot_ids, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        episode = {
            'query_embed': np.array(query_embed, dtype=np.float32).tolist(),
            'snippets': snippets[:5] if len(snippets) > 5 else snippets,
            'bot_ids': bot_ids[:8] if len(bot_ids) > 8 else bot_ids,
            'timestamp': timestamp,
            'strength': 1.0,
            'access_count': 0
        }
        self.episodes.append(episode)
        self.index.append(np.array(query_embed, dtype=np.float32).flatten())

        if len(self.episodes) > self.max_episodes:
            self.episodes.pop(0)
            self.index.pop(0)

    def query(self, query_embed, k=5):
        query_vec = np.array(query_embed, dtype=np.float32).flatten()
        if len(self.index) == 0:
            return []

        scores = []
        for i, idx_vec in enumerate(self.index):
            vec = np.array(idx_vec, dtype=np.float32).flatten()
            sim = np.dot(query_vec, vec)
            norm = np.linalg.norm(query_vec) * np.linalg.norm(vec) + 1e-8
            sim = sim / norm
            ep = self.episodes[i]
            decays = ep['strength']
            scores.append((sim * decays, i))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in scores[:k]:
            ep = self.episodes[idx]
            ep['access_count'] += 1
            ep['strength'] = min(1.0, ep['strength'] + 0.05)
            results.append(ep)
        return results

    def decay_step(self, hours_passed=1):
        factor = self.decay_rate ** (hours_passed / self.decay_unit_hours)
        for ep in self.episodes:
            ep['strength'] *= factor

    def save(self, path):
        data = {
            'dim': self.dim,
            'max_episodes': self.max_episodes,
            'decay_rate': self.decay_rate,
            'episodes': self.episodes,
            'index': [v.tolist() if isinstance(v, np.ndarray) else v for v in self.index]
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
        self.dim = data['dim']
        self.max_episodes = data['max_episodes']
        self.decay_rate = data['decay_rate']
        self.episodes = data['episodes']
        self.index = [np.array(v, dtype=np.float32) for v in data['index']]


class ResonanceEngine:
    def __init__(self, dim=128, n_bots=32, learning_rate=0.01):
        self.dim = dim
        self.n_bots = n_bots
        self.lr = learning_rate
        self.routing = np.random.randn(dim, n_bots).astype(np.float32) * 0.1
        self.counts = np.zeros((dim, n_bots), dtype=np.int32)

    def update(self, query_embed, bot_id, success):
        q = np.array(query_embed, dtype=np.float32).flatten()
        if bot_id >= self.n_bots:
            return
        for d in range(self.dim):
            delta = self.lr * (1.0 if success else -0.5) * q[d]
            self.routing[d, bot_id] += delta
            self.counts[d, bot_id] += 1

    def route(self, query_embed, top_k=3):
        q = np.array(query_embed, dtype=np.float32).flatten()
        scores = q @ self.routing
        scores = np.clip(scores, -1, 1)
        top_idx = np.argsort(scores)[::-1][:top_k]
        return [(int(idx), float(scores[idx])) for idx in top_idx]

    def save(self, path):
        np.savez(path, routing=self.routing, counts=self.counts)

    def load(self, path):
        data = np.load(path)
        self.routing = data['routing']
        self.counts = data['counts']


class DreamEngine:
    def __init__(self, hippocampus, resonance, batch_size=100, trigger_idle_min=300):
        self.hippocampus = hippocampus
        self.resonance = resonance
        self.batch_size = batch_size
        self.trigger_idle_min = trigger_idle_min
        self.last_dream = 0
        self.heuristics = []

    def consolidate(self, n_recent=100):
        if not self.hippocampus.episodes:
            return
        recent = self.hippocampus.episodes[-n_recent:] if len(self.hippocampus.episodes) > n_recent else self.hippocampus.episodes

        query_types = {}
        for ep in recent:
            bots = tuple(ep['bot_ids'])
            key = str(bots)
            if key not in query_types:
                query_types[key] = {'count': 0, 'total_strength': 0, 'bot_ids': bots}
            query_types[key]['count'] += 1
            query_types[key]['total_strength'] += ep['strength']

        for key, info in query_types.items():
            if info['count'] >= 3:
                heuristic = {
                    'pattern': list(info['bot_ids']),
                    'frequency': info['count'],
                    'avg_strength': info['total_strength'] / info['count'],
                    'type': 'dispatch_pattern'
                }
                self.heuristics.append(heuristic)

        for ep in recent:
            if time.time() - ep['timestamp'] > 3600 * 24 * 7:
                ep['strength'] *= 0.5

    def decay_old(self, threshold_days=30):
        cutoff = time.time() - threshold_days * 86400
        self.hippocampus.episodes = [
            ep for ep in self.hippocampus.episodes
            if ep['timestamp'] > cutoff or ep['strength'] > 0.3
        ]

    def run_full_cycle(self):
        self.consolidate()
        self.decay_old()
        self.last_dream = time.time()
        return {'heuristics': len(self.heuristics), 'episodes': len(self.hippocampus.episodes)}
