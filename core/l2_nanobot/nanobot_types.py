from enum import Enum
from dataclasses import dataclass, field
import numpy as np
import json
import hashlib
from collections import OrderedDict
from typing import List, Optional

class MessageType(Enum):
    SEARCH = 'SEARCH'
    EXTRACT = 'EXTRACT'
    VERIFY = 'VERIFY'
    CACHE_HIT = 'CACHE_HIT'
    RESULT = 'RESULT'
    CONFLICT = 'CONFLICT'

@dataclass
class Message:
    source_id: int
    target_id: int
    pheromone: np.ndarray
    type: MessageType
    payload: dict
    ttl: int

    def encode(self):
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'pheromone': self.pheromone.tolist(),
            'type': self.type.value,
            'payload': self.payload,
            'ttl': self.ttl
        }

@dataclass
class CacheEntry:
    url: str
    text: str
    embed: np.ndarray
    timestamp: float
    bot_id: int

    def encode(self):
        return {
            'url': self.url,
            'text': self.text,
            'embed': self.embed.tolist(),
            'timestamp': self.timestamp,
            'bot_id': self.bot_id
        }
