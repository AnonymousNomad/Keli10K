from core.l2_nanobot.nanobot_base import BaseNanobot
from core.l2_nanobot.nanobot_types import Message, MessageType, CacheEntry
import numpy as np
import time
from typing import List

class NanobotSwarm:
    def __init__(self, bots=None):
        self.bots = {}
        self.bot_list = []
        if bots:
            for bot in bots:
                self.register(bot)

    def register(self, bot):
        self.bots[bot.bot_id] = bot
        self.bot_list.append(bot)
        print(f"  Registered bot {bot.bot_id}: {bot.domain}")

    def dispatch(self, query_embed, top_k=3):
        if not self.bot_list:
            return []
        scores = []
        for bot in self.bot_list:
            sim = np.dot(query_embed, bot.query_to_embed(str(bot.bot_id)))
            sim = sim / (np.linalg.norm(query_embed) * np.linalg.norm(np.ones(128)) + 1e-8)
            scores.append((sim, bot))
        scores.sort(key=lambda x: x[0], reverse=True)
        selected = scores[:top_k]

        messages = []
        for sim, bot in selected:
            msg = Message(
                source_id=-1,
                target_id=bot.bot_id,
                pheromone=query_embed,
                type=MessageType.SEARCH,
                payload={'query': f'query_for_bot_{bot.bot_id}'},
                ttl=3
            )
            messages.append(msg)
        return messages

    def execute(self, msg):
        bot = self.bots.get(msg.target_id)
        if bot is None:
            return Message(
                source_id=-1, target_id=msg.source_id,
                pheromone=np.zeros(128, dtype=np.float32),
                type=MessageType.CONFLICT,
                payload={'error': f'Bot {msg.target_id} not found'},
                ttl=0
            )
        result = bot.handle_message(msg)
        return result

    def execute_batch(self, messages):
        results = []
        for msg in messages:
            if msg.ttl <= 0:
                continue
            result = self.execute(msg)
            results.append(result)
        return results

    def pheromone_write(self, mesh_state, msg):
        entry = {
            'query_embed': msg.pheromone.tolist(),
            'source': msg.source_id,
            'target': msg.target_id,
            'type': msg.type.value,
            'timestamp': time.time()
        }
        mesh_state.append(entry)

    def pheromone_read(self, query_embed, mesh_state, k=5):
        candidates = []
        for entry in mesh_state:
            stored = np.array(entry['query_embed'])
            sim = np.dot(query_embed, stored)
            norm = np.linalg.norm(query_embed) * np.linalg.norm(stored) + 1e-8
            candidates.append((sim / norm, entry))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:k]
