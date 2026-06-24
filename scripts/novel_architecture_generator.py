"""
Novel Architecture Generator — Keli invents new software patterns.
Each generator produces working code that combines patterns in novel ways.
"""
import random, json
from typing import List

class ArchitectureGenerator:
    """Generates novel software architectures by combining existing patterns."""

    patterns = {
        "architectural": [
            "microservice", "monolith", "serverless", "event-driven",
            "pipeline", "layered", "hexagonal", "clean", "onion",
            "CQRS", "event-sourcing", "saga", "pub-sub", "peer-to-peer"
        ],
        "data": [
            "SQL", "NoSQL", "graph", "time-series", "vector",
            "key-value", "document", "columnar", "stream"
        ],
        "paradigm": [
            "OOP", "functional", "reactive", "declarative",
            "aspect-oriented", "data-oriented", "actor-based"
        ],
        "deployment": [
            "containerized", "bare-metal", "edge", "hybrid-cloud",
            "multi-cloud", "distributed", "embedded"
        ],
        "novel_concepts": [
            "nanobot", "swarm", "consensus", "voting", "emergent",
            "self-healing", "adaptive", "evolving", "symbiotic",
            "holographic", "fractal", "recursive", "hive-mind"
        ]
    }

    @staticmethod
    def combine(*parts):
        """Combine multiple architecture patterns into a novel hybrid."""
        return "-".join(parts) + "-architecture"

    @staticmethod
    def generate_architecture_name() -> str:
        g = ArchitectureGenerator
        p = g.patterns
        style = random.choice(p["novel_concepts"])
        base = random.choice(p["architectural"])
        data = random.choice(p["data"])
        return f"{style}-{data}-{base}"

    @staticmethod
    def generate_novel_pattern() -> dict:
        name = ArchitectureGenerator.generate_architecture_name()
        g = ArchitectureGenerator
        p = g.patterns

        primary = random.choice(p["architectural"])
        secondary = random.choice(p["architectural"])
        data_style = random.choice(p["data"])
        paradigm = random.choice(p["paradigm"])
        deployment = random.choice(p["deployment"])
        concept = random.choice(p["novel_concepts"])

        description = f"A {concept} {data_style} {primary} architecture with {secondary} event handling, using {paradigm} design, deployed as {deployment}"

        code = ArchitectureGenerator._generate_code(name, concept, data_style, primary, secondary, paradigm)

        return {
            "name": name,
            "description": description,
            "components": {
                "primary_pattern": primary,
                "secondary_pattern": secondary,
                "data_layer": data_style,
                "paradigm": paradigm,
                "deployment": deployment,
                "novel_concept": concept
            },
            "code": code
        }

    @staticmethod
    def _generate_code(name, concept, data_style, primary, secondary, paradigm):
        g = ArchitectureGenerator
        class_name = name.replace("-", " ").title().replace(" ", "")

        if concept in ["nanobot", "swarm", "hive-mind"]:
            return g._gen_swarm_arch(class_name, data_style, primary)
        elif concept in ["self-healing", "adaptive"]:
            return g._gen_adaptive_arch(class_name, data_style, primary)
        elif concept in ["fractal", "recursive"]:
            return g._gen_recursive_arch(class_name, data_style, primary)
        elif concept in ["holographic"]:
            return g._gen_holographic_arch(class_name, data_style)
        elif concept in ["emergent"]:
            return g._gen_emergent_arch(class_name, data_style, primary, secondary)
        else:
            return g._gen_default_arch(class_name, data_style, primary, secondary)

    @staticmethod
    def _gen_swarm_arch(name, data_style, primary):
        return f'''"""
{name} — Swarm-based {primary} architecture with parallel agent coordination.
"""

import asyncio, random, uuid, time
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class SwarmAgent:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: str = "worker"
    state: dict = field(default_factory=dict)
    load: float = 0.0
    alive: bool = True

    async def execute(self, task: dict) -> Any:
        self.load += 1
        await asyncio.sleep(random.uniform(0.01, 0.05))
        result = {{"agent": self.id, "task": task["type"], "status": "done",
                  "data": task.get("data", {{}}), "timestamp": time.time()}}
        self.load -= 1
        return result

class SwarmCoordinator:
    """Coordinates swarm agents using consensus-based task distribution."""

    def __init__(self, n_agents: int = 10):
        self.agents = [SwarmAgent(role=random.choice(["worker", "scout", "validator"]))
                      for _ in range(n_agents)]
        self.task_queue = asyncio.Queue()
        self.results = []

    async def distribute(self, task: dict):
        available = [a for a in self.agents if a.load < 3 and a.alive]
        if not available:
            await asyncio.sleep(0.1)
            return
        agent = min(available, key=lambda a: a.load)
        result = await agent.execute(task)
        self.results.append(result)
        return result

    async def swarm_consensus(self, tasks: list[dict]) -> list:
        coros = [self.distribute(t) for t in tasks]
        return await asyncio.gather(*coros)

    def health_report(self) -> dict:
        return {{
            "agents_alive": sum(1 for a in self.agents if a.alive),
            "total_load": sum(a.load for a in self.agents),
            "tasks_completed": len(self.results),
            "agents": [{{"id": a.id, "role": a.role, "load": a.load, "alive": a.alive}}
                      for a in self.agents]
        }}

# === Example Usage ===
async def demo():
    swarm = SwarmCoordinator(10)
    tasks = [{{"type": "process", "data": {{"id": i, "value": i * 2}}}}
             for i in range(20)]
    results = await swarm.swarm_consensus(tasks)
    print(f"Swarm processed {{len(results)}} tasks")
    print(f"Health: {{swarm.health_report()}}")

if __name__ == "__main__":
    asyncio.run(demo())'''

    @staticmethod
    def _gen_adaptive_arch(name, data_style, primary):
        return f'''"""
{name} — Self-adaptive {primary} architecture that optimizes in real-time.
"""

import time, random, statistics
from dataclasses import dataclass
from typing import Any

@dataclass
class AdaptiveComponent:
    name: str
    capacity: int = 100
    load: float = 0.0
    latency_ms: list = None

    def __post_init__(self):
        self.latency_ms = []

    def handle(self, request: Any) -> dict:
        t0 = time.time()
        simulated = random.uniform(1, 10)
        time.sleep(simulated / 1000)
        self.load += 1
        self.latency_ms.append((time.time() - t0) * 1000)
        return {{"component": self.name, "result": request, "latency": simulated}}

    @property
    def avg_latency(self):
        return statistics.mean(self.latency_ms[-100:]) if self.latency_ms else 0

class AdaptiveArchitecture:
    """Dynamically routes requests based on component performance."""

    def __init__(self):
        self.components = [
            AdaptiveComponent(f"node-{{i}}", capacity=random.randint(50, 200))
            for i in range(8)
        ]
        self.routing_table = {{c.name: 1.0 for c in self.components}}

    def update_routes(self):
        total_latency = sum(c.avg_latency for c in self.components) or 1
        for c in self.components:
            if c.avg_latency > 0:
                self.routing_table[c.name] = 1.0 / (c.avg_latency / total_latency)
        norm = sum(self.routing_table.values()) or 1
        for k in self.routing_table:
            self.routing_table[k] /= norm

    def route(self, request: Any) -> dict:
        self.update_routes()
        best = max(self.components, key=lambda c: self.routing_table[c.name] * c.capacity)
        return best.handle(request)

    def optimize(self):
        """Scale components based on load patterns."""
        avg_load = statistics.mean([c.load for c in self.components])
        for c in self.components:
            if c.load > avg_load * 1.5:
                c.capacity = int(c.capacity * 1.2)
            elif c.load < avg_load * 0.5 and c.capacity > 50:
                c.capacity = int(c.capacity * 0.9)

# === Example ===
def demo():
    arch = AdaptiveArchitecture()
    for i in range(50):
        result = arch.route({{"id": i, "type": "request"}})
    arch.optimize()
    print(f"Components: {{len(arch.components)}}")
    for c in arch.components:
        print(f"  {{c.name}}: load={{c.load}}, latency={{c.avg_latency:.1f}}ms, cap={{c.capacity}}")

if __name__ == "__main__":
    demo()'''

    @staticmethod
    def _gen_recursive_arch(name, data_style, primary):
        return f'''"""
{name} — Recursive {primary} architecture where components contain sub-components.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import time, random, uuid

@dataclass
class RecursiveNode:
    name: str
    level: int = 0
    children: list = field(default_factory=list)
    max_children: int = 3
    max_depth: int = 4

    def build(self, current_depth: int = 0):
        if current_depth >= self.max_depth:
            return
        n = random.randint(1, self.max_children)
        for i in range(n):
            child = RecursiveNode(
                name=f"{{self.name}}/sub-{{i}}",
                level=current_depth + 1,
                max_children=self.max_children,
                max_depth=self.max_depth
            )
            child.build(current_depth + 1)
            self.children.append(child)

    def execute(self, context: dict = None) -> list[dict]:
        if context is None:
            context = {{}}
        results = [{{"node": self.name, "level": self.level, "action": "process",
                    "id": str(uuid.uuid4())[:8], "timestamp": time.time()}}]
        for child in self.children:
            results.extend(child.execute(context))
        return results

    @property
    def total_nodes(self) -> int:
        return 1 + sum(c.total_nodes for c in self.children)

    def to_dict(self) -> dict:
        return {{
            "name": self.name,
            "level": self.level,
            "children": [c.to_dict() for c in self.children]
        }}

# === Example ===
def demo():
    root = RecursiveNode("system", max_depth=3, max_children=3)
    root.build()
    print(f"Recursive architecture: {{root.total_nodes}} total nodes")

    import json
    structure = root.to_dict()
    print(json.dumps(structure, indent=2)[:500] + "...")

    results = root.execute()
    print(f"Execution produced {{len(results)}} results")

if __name__ == "__main__":
    demo()'''

    @staticmethod
    def _gen_holographic_arch(name, data_style):
        return f'''"""
{name} — Holographic architecture: every component contains the whole system state.
"""

import hashlib, json, time, copy
from dataclasses import dataclass, field
from typing import Any

@dataclass
class HolographicFragment:
    name: str
    state_hash: str = ""
    system_state: dict = field(default_factory=dict)

    def sync(self, global_state: dict):
        self.system_state = copy.deepcopy(global_state)
        self.state_hash = hashlib.sha256(
            json.dumps(global_state, sort_keys=True).encode()
        ).hexdigest()[:16]

    def process(self, input_data: Any) -> dict:
        prev_hash = self.state_hash
        self.system_state["last_input"] = input_data
        self.system_state["processed_by"] = self.name
        self.system_state["timestamp"] = time.time()
        self.sync(self.system_state)
        return {{
            "fragment": self.name,
            "previous_hash": prev_hash,
            "new_hash": self.state_hash,
            "state_size": len(json.dumps(self.system_state)),
            "result": f"Processed by {{self.name}} with holographic sync"
        }}

class HolographicSystem:
    """Every fragment contains the full state — true holographic design."""

    def __init__(self, n_fragments: int = 5):
        self.global_state = {{"started": time.time(), "events": [], "count": 0}}
        self.fragments = [HolographicFragment(f"frag-{{i}}") for i in range(n_fragments)]
        for f in self.fragments:
            f.sync(self.global_state)

    def broadcast(self, input_data: Any) -> list[dict]:
        self.global_state["count"] += 1
        self.global_state["events"].append({{"time": time.time(), "data": input_data}})
        results = []
        for f in self.fragments:
            f.sync(self.global_state)
            results.append(f.process(input_data))
        return results

    def verify_integrity(self) -> bool:
        """All fragments should agree on state hash."""
        if not self.fragments:
            return True
        first_hash = self.fragments[0].state_hash
        return all(f.state_hash == first_hash for f in self.fragments)

# === Example ===
def demo():
    system = HolographicSystem(5)
    results = system.broadcast("hello holographic world")
    print(f"Integrity: {{system.verify_integrity()}}")
    for r in results:
        print(f"  {{r['fragment']}}: hash={{r['new_hash']}}, state={{r['state_size']}}b")

if __name__ == "__main__":
    demo()'''

    @staticmethod
    def _gen_emergent_arch(name, data_style, primary, secondary):
        return f'''"""
{name} — Emergent {primary}/{secondary} architecture where behavior self-organizes.
"""

import random, time, statistics
from dataclasses import dataclass, field
from typing import Any

@dataclass
class MicroService:
    name: str
    behavior: str = ""
    connections: list = field(default_factory=list)
    state: Any = 0

    def act(self, neighbors: list) -> Any:
        """Simple rule-based behavior that produces complex outcomes."""
        avg = statistics.mean([n.state for n in neighbors]) if neighbors else 0
        if self.state < avg:
            self.state += random.uniform(0, 1)
        else:
            self.state -= random.uniform(0, 1)
        self.state = max(0, min(100, self.state))
        return self.state

class EmergentSystem:
    """Complex behavior emerges from simple local rules."""

    def __init__(self, n_services: int = 20):
        self.services = [
            MicroService(f"srv-{{i}}", random.choice(["gatherer", "processor", "distributor"]))
            for i in range(n_services)
        ]
        # Random network topology
        for s in self.services:
            s.connections = random.sample(
                [x for x in self.services if x != s],
                random.randint(1, 5)
            )

    def step(self) -> dict:
        for s in self.services:
            s.act(s.connections)
        states = [s.state for s in self.services]
        return {{
            "mean": statistics.mean(states),
            "std": statistics.stdev(states) if len(states) > 1 else 0,
            "min": min(states),
            "max": max(states)
        }}

    def simulate(self, steps: int = 100) -> list[dict]:
        history = []
        for _ in range(steps):
            snap = self.step()
            history.append(snap)
        return history

    def analyze(self, history: list[dict]) -> dict:
        means = [h["mean"] for h in history]
        return {{
            "services": len(self.services),
            "steps": len(history),
            "final_mean": means[-1] if means else 0,
            "converged": statistics.stdev(means[-10:]) < 1 if len(means) >= 10 else False,
            "emergent_behavior": "stable" if statistics.stdev(means[-20:]) < 2 else "oscillating"
        }}

# === Example ===
def demo():
    system = EmergentSystem(30)
    history = system.simulate(200)
    analysis = system.analyze(history)
    print(f"Emergent system: {{analysis['services']}} services")
    print(f"  Converged: {{analysis['converged']}}")
    print(f"  Behavior: {{analysis['emergent_behavior']}}")
    print(f"  Final state: {{analysis['final_mean']:.1f}}")

if __name__ == "__main__":
    demo()'''

    @staticmethod
    def _gen_default_arch(name, data_style, primary, secondary):
        return f'''"""
{name} — Hybrid {primary}/{secondary} architecture with {data_style} storage.
"""

from dataclasses import dataclass, field
from typing import Any
import time, random

@dataclass
class HybridComponent:
    name: str
    pattern: str = ""
    data: dict = field(default_factory=dict)

    def process(self, request: Any) -> dict:
        self.data["last_request"] = request
        self.data["timestamp"] = time.time()
        return {{"component": self.name, "pattern": self.pattern, "result": request}}

class HybridArchitecture:
    """Combines multiple architectural patterns into a unified system."""

    def __init__(self):
        self.components = [
            HybridComponent(f"{{primary}}-handler", pattern="{primary}"),
            HybridComponent(f"{{secondary}}-worker", pattern="{secondary}"),
            HybridComponent("data-layer", pattern="{data_style}"),
        ]

    def execute(self, input_data: Any) -> list[dict]:
        results = []
        for comp in self.components:
            results.append(comp.process(input_data))
        return results

# === Example ===
def demo():
    arch = HybridArchitecture()
    results = arch.execute({{"task": "process", "value": 42}})
    for r in results:
        print(f"  {{r['component']}} ({{r['pattern']}}): {{r['result']}}")

if __name__ == "__main__":
    demo()'''


def generate_novel_dataset(n_examples=100000):
    """Generate training data from novel architectures."""
    gen = ArchitectureGenerator
    examples = []
    for _ in range(n_examples):
        arch = gen.generate_novel_pattern()
        examples.append({
            "input": f"design a {arch['name']}",
            "target": arch['code']
        })
        examples.append({
            "input": arch['description'],
            "target": arch['code']
        })
        # Add variant
        arch2 = gen.generate_novel_pattern()
        examples.append({
            "input": f"create a {arch2['name']} system",
            "target": arch2['code']
        })
    return examples

if __name__ == "__main__":
    print("=== Novel Architecture Generator ===\n")
    for _ in range(3):
        arch = ArchitectureGenerator.generate_novel_pattern()
        print(f"  {arch['name']}")
        print(f"  Description: {arch['description']}")
        lines = arch['code'].count('\\n')
        print(f"  Code: {lines} lines\n")
