import numpy as np
import hashlib
import time
from collections import OrderedDict
from core.l2_nanobot.nanobot_types import Message, MessageType, CacheEntry
from typing import List, Optional

class BaseNanobot:
    def __init__(self, bot_id, domain, schema):
        self.bot_id = bot_id
        self.domain = domain
        self.domain_hash = hashlib.sha256(domain.encode()).digest()
        self.schema = schema
        self.cache = OrderedDict()
        self.cache_max = 100
        self.success_rate = 1.0
        self.last_active = 0

    def query_to_embed(self, query_str):
        seed = abs(hash(query_str + self.domain)) % (2**32)
        rng = np.random.RandomState(seed)
        return rng.randn(128).astype(np.float32)

    def simulate_fetch(self, query_str):
        seed = abs(hash(query_str + str(self.bot_id))) % (2**32)
        rng = np.random.RandomState(seed)
        n_results = int(rng.randint(1, 4))
        results = []
        for i in range(n_results):
            url = f"https://{self.domain}/{self.bot_id}_{int(time.time())}_{i}"
            text = f"Mock result from {self.domain}: {query_str} result #{i}"
            entries = [
                f"Found reference for {query_str}",
                f"Documentation snippet {i}: relevant content",
                f"Example usage pattern matched"
            ]
            embed = self.query_to_embed(query_str + str(i))
            entry = CacheEntry(
                url=url,
                text=entries[i % len(entries)],
                embed=embed,
                timestamp=time.time(),
                bot_id=self.bot_id
            )
            results.append(entry)
            self._cache_put(url, entry)
        return results

    def update_success(self, rate):
        self.success_rate = 0.9 * self.success_rate + 0.1 * rate
        self.last_active = time.time()

    def _cache_get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def _cache_put(self, key, value):
        self.cache[key] = value
        if len(self.cache) > self.cache_max:
            self.cache.popitem(last=False)

    def handle_message(self, msg):
        if msg.ttl <= 0:
            return Message(
                source_id=self.bot_id,
                target_id=msg.source_id,
                pheromone=np.zeros(128, dtype=np.float32),
                type=MessageType.CONFLICT,
                payload={'error': 'TTL expired'},
                ttl=0
            )
        query = msg.payload.get('query', '')
        cached = self._cache_get(query)
        if cached:
            return Message(
                source_id=self.bot_id,
                target_id=msg.source_id,
                pheromone=self.query_to_embed(query),
                type=MessageType.CACHE_HIT,
                payload={'entry': cached.encode()},
                ttl=msg.ttl - 1
            )
        results = self.simulate_fetch(query)
        return Message(
            source_id=self.bot_id,
            target_id=msg.source_id,
            pheromone=self.query_to_embed(query),
            type=MessageType.RESULT,
            payload={'results': [r.encode() for r in results]},
            ttl=msg.ttl - 1
        )
