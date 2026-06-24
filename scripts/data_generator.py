import random
import json
import hashlib
from pathlib import Path

BOS = 2
EOS = 1
PAD = 0
PLAN = 4
EXEC = 5
REFLECT = 6
TOOL_CALL = 7
TOOL_RESULT = 8
CITE = 9
UNSURE = 10
DECOMP = 11
DISPATCH = 12
SYNTH = 13
SEP = 14
FIRST_TOKEN = 15

P1_TOPICS = [
    "manage state in React", "style with CSS Grid", "fetch data in JavaScript",
    "use Python list comprehensions", "create a React component", "handle forms in HTML",
    "sort an array in JavaScript", "use async await in Python", "build a REST API with Flask",
    "implement binary search", "use CSS Flexbox", "create a responsive navbar",
    "handle errors in async functions", "use localStorage in JavaScript",
    "create a React custom hook", "use Python decorators", "deploy a Node.js app",
    "use SQLite in Python", "create CSS animations", "use React Context",
]
P1_PLANS = [
    "Check the official documentation for patterns and best practices",
    "Decompose the problem into smaller steps and implement each one",
    "Search the knowledge base for relevant examples and adapt them",
    "Use standard library functions and verify with unit tests",
    "Look up the API reference and apply the recommended approach",
]
P1_EXECS = [
    "The standard approach uses built-in functions and well documented patterns",
    "Following the community best practices and official guides yields reliable results",
    "The implementation follows the principle of least surprise and is thoroughly tested",
    "Each step is validated against known working examples from the documentation",
    "The solution leverages established patterns and avoids anti patterns",
]

P2_TASKS = [
    "Build a todo app with React", "Create a weather dashboard", "Write a Python CLI tool",
    "Build a chat application", "Create a markdown editor",
    "Build a real time dashboard", "Create a file upload service", "Write a web scraper",
    "Build a notification system", "Create a drag and drop interface",
    "Build a data visualization", "Create a user authentication system",
]
P2_SUBTASKS = [
    ["HTML structure", "CSS styling", "JavaScript logic", "State management"],
    ["Component tree", "Data fetching", "State updates", "UI rendering"],
    ["Entry point", "Argument parser", "Business logic", "Output formatting"],
    ["WebSocket handler", "Message queue", "User presence", "History storage"],
    ["Editor component", "Preview pane", "Toolbar", "Export function"],
    ["Data source", "Real time updates", "Chart rendering", "Auto refresh"],
    ["Upload endpoint", "File validation", "Storage backend", "Status reporting"],
    ["Request handler", "Parser module", "Data extraction", "Export pipeline"],
    ["Notification model", "Delivery service", "Preference storage", "UI display"],
    ["Drag handler", "Drop zone", "Reorder logic", "State sync"],
    ["Data pipeline", "Chart config", "Rendering engine", "Interaction layer"],
    ["Registration form", "Login handler", "Session management", "Protected routes"],
]

P3_BOTS = [
    {"id": "react-docs", "queries": ["useState hook", "useEffect cleanup", "React Context", "custom hooks", "JSX syntax"]},
    {"id": "python-docs", "queries": ["list comprehension", "decorator pattern", "async await", "context manager", "generator"]},
    {"id": "mdn-docs", "queries": ["fetch API", "CSS Grid", "Flexbox layout", "Promises", "localStorage"]},
    {"id": "github-docs", "queries": ["Git workflow", "PR template", "issue tracking", "actions CI", "repo setup"]},
]

P4_SNIPPETS = [
    ["useState returns value and setter pair", "State updates trigger re render", "Functional updates prevent stale state"],
    ["CSS Grid uses display grid", "Grid template columns defines layout", "Gap property controls spacing"],
    ["Fetch returns a Promise", "Response json parses the body", "Async await simplifies the chain"],
    ["Python lists are ordered and mutable", "List comprehensions are concise", "Slicing creates new lists"],
    ["React keys should be unique and stable", "Keys help identify changed items", "Index as key can cause bugs"],
    ["CSS Flexbox is one dimensional", "Justify content aligns main axis", "Align items aligns cross axis"],
    ["UseEffect runs after render", "Cleanup function prevents memory leaks", "Dependencies array controls execution"],
    ["Context provides a way to share data", "Create context using createContext", "Use context to consume values"],
    ["JavaScript Promises have three states", "Then chains handle resolution", "Catch handles rejection"],
    ["Python decorators wrap functions", "Functools wraps preserves metadata", "Decorators enable cross cutting concerns"],
]
P4_SOURCES = [
    "React Docs", "MDN Web Docs", "Python Docs",
]
P4_YEARS = ["2024", "2025", "2026"]
P4_URLS = [
    "https://react.dev", "https://developer.mozilla.org",
    "https://docs.python.org",
]

P5_TEMPLATES = [
    {"draft": "This component uses state incorrectly", "error": "Missing dependency array in useEffect",
     "fix": "Add dependency array to useEffect to prevent infinite re renders"},
    {"draft": "Python is slow for this task", "error": "Claim without benchmark data",
     "fix": "Include time complexity analysis and performance benchmarks"},
    {"draft": "CSS Grid works everywhere", "error": "Overly broad unsupported claim",
     "fix": "CSS Grid works in all modern browsers verify browser support"},
    {"draft": "Just use a for loop", "error": "Does not consider functional alternatives",
     "fix": "Consider map filter or reduce which are more idiomatic for transformations"},
    {"draft": "The API is broken", "error": "Vague without specific error details",
     "fix": "Check HTTP status code and error response body for specific error message"},
]


def _stable_rng(seed_str):
    h = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    return random.Random(h)


def _random_ids(rng, min_n=3, max_n=8):
    n = rng.randint(min_n, max_n)
    return [rng.randint(FIRST_TOKEN, 8191) for _ in range(n)]


def generate_p1(n=10000):
    data = []
    for i in range(n):
        rng = _stable_rng(f"p1_{i}")
        topic = rng.choice(P1_TOPICS)
        plan = rng.choice(P1_PLANS)
        exec_text = rng.choice(P1_EXECS)
        source = rng.choice(P4_SOURCES)
        url = rng.choice(P4_URLS)
        year = rng.choice(P4_YEARS)

        input_ids = [BOS] + [FIRST_TOKEN + (ord(c) % 8000) for c in topic] + [SEP]
        target_ids = [PLAN] + [FIRST_TOKEN + (ord(c) % 8000) for c in plan] + [EXEC] + \
                     [FIRST_TOKEN + (ord(c) % 8000) for c in exec_text] + [CITE] + \
                     [FIRST_TOKEN + (ord(c) % 8000) for c in f"{source} {url} {year}"] + [EOS]
        input_ids = input_ids[:128]
        target_ids = target_ids[:384]

        data.append({"input_ids": input_ids, "target_ids": target_ids, "mode": "plan"})
    return data


def generate_p2(n=10000):
    data = []
    for i in range(n):
        rng = _stable_rng(f"p2_{i}")
        task = rng.choice(P2_TASKS)
        subs = rng.choice(P2_SUBTASKS)
        rng.shuffle(subs)

        input_ids = [BOS] + [FIRST_TOKEN + (ord(c) % 8000) for c in task] + [SEP]
        target_ids = [PLAN] + [DECOMP]
        for sub in subs:
            target_ids += [FIRST_TOKEN + (ord(c) % 8000) for c in sub] + [SEP]
        target_ids += [EOS]
        input_ids = input_ids[:128]
        target_ids = target_ids[:384]

        data.append({"input_ids": input_ids, "target_ids": target_ids, "mode": "plan"})
    return data


def generate_p3(n=10000):
    data = []
    for i in range(n):
        rng = _stable_rng(f"p3_{i}")
        bot = rng.choice(P3_BOTS)
        query = rng.choice(bot["queries"])

        input_ids = [BOS] + [FIRST_TOKEN + (ord(c) % 8000) for c in query] + [SEP]
        dispatch = json.dumps({"bot_id": bot["id"], "query": query,
                               "max_results": rng.randint(3, 10),
                               "freshness_days": rng.choice([30, 90, 365])})
        target_ids = [TOOL_CALL] + [FIRST_TOKEN + (ord(c) % 8000) for c in dispatch] + [TOOL_RESULT]
        mock_result = f"Found relevant documentation for {query}"
        target_ids += [FIRST_TOKEN + (ord(c) % 8000) for c in mock_result] + [EOS]
        input_ids = input_ids[:128]
        target_ids = target_ids[:384]

        data.append({"input_ids": input_ids, "target_ids": target_ids, "mode": "plan"})
    return data


def generate_p4(n=15000):
    data = []
    for i in range(n):
        rng = _stable_rng(f"p4_{i}")
        snippets = rng.choice(P4_SNIPPETS)
        rng.shuffle(snippets)
        source = rng.choice(P4_SOURCES)
        url = rng.choice(P4_URLS)
        year = rng.choice(P4_YEARS)

        input_ids = [BOS]
        for s in snippets:
            input_ids += [FIRST_TOKEN + (ord(c) % 8000) for c in s] + [CITE]
        input_ids += [SEP]
        input_ids = input_ids[:256]

        combined = " ".join(snippets[:2])
        target_ids = [EXEC] + [FIRST_TOKEN + (ord(c) % 8000) for c in combined] + \
                     [CITE] + [FIRST_TOKEN + (ord(c) % 8000) for c in f"{source} {url} {year}"] + [EOS]
        target_ids = target_ids[:384]

        data.append({"input_ids": input_ids, "target_ids": target_ids, "mode": "plan"})
    return data


def generate_p5(n=5000):
    data = []
    for i in range(n):
        rng = _stable_rng(f"p5_{i}")
        t = rng.choice(P5_TEMPLATES)
        source = rng.choice(P4_SOURCES)
        url = rng.choice(P4_URLS)
        year = rng.choice(P4_YEARS)

        input_ids = [BOS] + [FIRST_TOKEN + (ord(c) % 8000) for c in t["draft"]] + [SEP]
        input_ids = input_ids[:128]

        target_ids = [REFLECT] + [FIRST_TOKEN + (ord(c) % 8000) for c in t["error"]] + \
                     [EXEC] + [FIRST_TOKEN + (ord(c) % 8000) for c in t["fix"]] + \
                     [CITE] + [FIRST_TOKEN + (ord(c) % 8000) for c in f"{source} {url} {year}"] + [EOS]
        target_ids = target_ids[:384]

        data.append({"input_ids": input_ids, "target_ids": target_ids, "mode": "plan"})
    return data


def generate_build(n=1000):
    data = []
    territories = ["frontend", "backend", "data", "devops"]
    build_tasks = [
        "create a React component", "build an API endpoint", "write a data pipeline",
        "configure a deployment", "implement a form", "create a database schema",
    ]
    for i in range(n):
        rng = _stable_rng(f"build_{i}")
        task = rng.choice(build_tasks)
        terr = rng.choice(territories)
        input_ids = [BOS] + [FIRST_TOKEN + (ord(c) % 8000) for c in f"Build {task} for {terr}"] + [SEP]
        code_tokens = [FIRST_TOKEN + (ord(c) % 8000) for c in f"function implementation for {task} territory {terr}"]
        target_ids = [PLAN] + [FIRST_TOKEN + (ord(c) % 8000) for c in f"build {terr} {task}"] + \
                     [EXEC] + code_tokens + [EOS]
        input_ids = input_ids[:128]
        target_ids = target_ids[:384]
        data.append({"input_ids": input_ids, "target_ids": target_ids, "mode": "build"})
    return data


def save_jsonl(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    print(f"  Saved {len(data)} examples to {path}")


def generate_all(output_dir="data/generated"):
    sizes = {"p1": 10000, "p2": 10000, "p3": 10000, "p4": 15000, "p5": 5000, "build": 1000}
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    generators = {
        "p1": generate_p1, "p2": generate_p2, "p3": generate_p3,
        "p4": generate_p4, "p5": generate_p5, "build": generate_build,
    }

    for phase in ["p1", "p2", "p3", "p4", "p5", "build"]:
        n = sizes[phase]
        print(f"Generating {phase}: {n} samples...")
        data = generators[phase](n)
        save_jsonl(data, f"{output_dir}/{phase}.jsonl")

    all_data = []
    for phase in ["p1", "p2", "p3", "p4", "p5", "build"]:
        path = Path(output_dir) / f'{phase}.jsonl'
        if path.exists():
            with open(path) as f:
                all_data.extend([json.loads(line) for line in f if line.strip()])

    train = all_data[:int(len(all_data) * 0.9)]
    val = all_data[int(len(all_data) * 0.9):]
    save_jsonl(train, f"{output_dir}/train.jsonl")
    save_jsonl(val, f"{output_dir}/val.jsonl")
    print(f"Total: {len(all_data)} (train: {len(train)}, val: {len(val)})")
    print("All data generated.")


if __name__ == '__main__':
    generate_all()
