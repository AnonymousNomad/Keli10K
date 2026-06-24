#!/usr/bin/env python3
"""Keli10K 24-hour validation: generate 5K examples, train, test, report."""
import os, sys, json, math, time, random, hashlib, traceback
from pathlib import Path
import torch
import torch.nn.functional as F

sys.path.insert(0, '/tmp/opencode/snca')
sys.path.insert(0, '/tmp/opencode/snca/scripts')
from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from keli_10k import Keli10KModel

device = 'cuda' if torch.cuda.is_available() else 'cpu'
PAD, EOS, BOS = 0, 1, 2
SPECIAL = {'BOS': BOS, 'EOS': EOS, 'PAD': PAD}
tok = SNCATokenizer()

def t(text):
    return tok.encode(text, bos=False, eos=False)

OUT_DIR = '/tmp/opencode/snca/data/validate'
CKPT_DIR = '/tmp/opencode/snca/checkpoints'

# ============================================================
# DATA GENERATION — 5,000 examples
# ============================================================

# P1: 1,000 reasoning (code logic questions)
P1_DATA = [
    ("Why does useState cause re-renders?", "useState triggers a re-render when setState is called because React schedules a state update and re-renders the component to reflect the new state in the virtual DOM."),
    ("When should you use useReducer over useState?", "useReducer is better for complex state logic with multiple sub-values or when the next state depends on the previous one. It centralizes state transitions in a reducer function."),
    ("Why is useEffect cleanup important?", "useEffect cleanup prevents memory leaks by canceling subscriptions, clearing timers, and aborting fetch requests when the component unmounts or before the effect re-runs."),
    ("How does React reconciliation work?", "React compares virtual DOM trees using a diffing algorithm. It compares element types first, then keys, then props. If the type differs, it rebuilds the entire subtree."),
    ("Why should keys be stable and unique in lists?", "Keys help React identify which items changed, were added, or removed. Index-based keys cause bugs with insertions, deletions, and reordering because React reuses component instances incorrectly."),
    ("What is the event loop in JavaScript?", "The event loop continuously checks the call stack and task queues. When the call stack is empty, it pushes the first task from the microtask queue, then the macrotask queue, back to the call stack."),
    ("Why does typeof null return object?", "typeof null returns object due to a bug in the original JavaScript implementation where null was represented as a zero pointer, which was typed as object. It was never fixed for backward compatibility."),
    ("How do JavaScript closures work?", "A closure is created when a function retains access to variables from its outer scope even after the outer function has returned. Each function call creates a new closure with its own scope chain."),
    ("What is prototypal inheritance?", "Objects inherit from other objects via the prototype chain. When a property is accessed, JS walks the chain until found. Object.create and class syntax both use prototypal inheritance internally."),
    ("Why is async/await preferred over callbacks?", "Async/await makes asynchronous code read like synchronous code, reduces nesting, provides better error handling with try/catch, and avoids callback hell by flattening the control flow."),
    ("How does Python's GIL affect threading?", "The GIL prevents multiple threads from executing Python bytecode simultaneously. For CPU-bound tasks, multiprocessing is preferred. For I/O-bound tasks, threads still work because the GIL is released during I/O."),
    ("Why use __slots__ in Python classes?", "__slots__ reduces memory overhead by preventing __dict__ creation. Each instance uses a fixed-size array instead of a dictionary, saving memory in classes with many instances."),
    ("What is the difference between @staticmethod and @classmethod?", "@classmethod receives the class as the first argument and can access/modify class state. @staticmethod receives no implicit argument and is just a function namespaced in the class."),
    ("How do Python context managers work?", "Context managers implement __enter__ and __exit__ methods. The with statement calls __enter__, executes the block, then calls __exit__ even if an exception occurs, ensuring cleanup."),
    ("What is duck typing in Python?", "Duck typing means an object's suitability is determined by the presence of methods/properties, not its type. If it walks like a duck and quacks like a duck, it is treated as a duck."),
    ("How does CSS specificity work?", "Specificity is calculated as inline > ID > class > element. !important overrides all. When selectors have equal specificity, the last declaration wins. Higher specificity overrides lower."),
    ("What is the CSS box model?", "Every element is a box with content, padding, border, and margin. box-sizing:border-box includes padding and border in the width calculation, making layout easier."),
    ("How does Flexbox sizing work?", "Flexbox distributes space along the main axis. flex-grow defines how remaining space is distributed, flex-shrink defines how items shrink when there's not enough space, flex-basis sets initial size."),
    ("What is z-index stacking context?", "z-index only works on positioned elements. Each stacking context is isolated: child elements within one context are stacked among themselves before comparing to siblings in the parent context."),
    ("How do media queries work with mobile-first design?", "Mobile-first starts with base styles for small screens, then uses min-width media queries to add complexity for larger screens. This ensures the base experience works everywhere."),
]

P2_DATA = [
    ("Build a todo app", ["Create the HTML structure with an input form and a list container", "Style the app with CSS for a clean, responsive layout", "Add JavaScript to handle adding todos from the input field", "Implement todo completion toggle with click events", "Add delete functionality to remove todos from the list", "Store todos in localStorage for persistence across page reloads"]),
    ("Build a weather dashboard", ["Design the UI layout with a search bar and current conditions display", "Integrate with a weather API using fetch for real-time data", "Parse and display temperature, humidity, and wind speed", "Add a 5-day forecast section with icons and temperatures", "Implement error handling for invalid city names and network failures"]),
    ("Build a user authentication system", ["Create a registration form with email, password, and validation", "Implement password hashing with bcrypt on the backend", "Build a login endpoint that returns a JWT token", "Add protected routes that verify JWT on each request", "Create a React auth context to manage login state on the frontend"]),
    ("Build a real-time chat application", ["Set up a WebSocket server for bidirectional communication", "Create a connection manager that handles multiple rooms", "Build the frontend chat UI with message bubbles and timestamps", "Implement typing indicators and online presence detection", "Add message persistence to a database for history"]),
    ("Build a REST API for a blog", ["Design the database schema with users, posts, and comments tables", "Create CRUD endpoints for posts with proper HTTP methods", "Add pagination with offset and limit query parameters", "Implement authentication for protected write operations", "Add input validation and proper error response formatting"]),
    ("Build a drag-and-drop kanban board", ["Create the board layout with columns representing workflow stages", "Implement drag handlers with HTML5 drag and drop API", "Add drop zones that accept cards and update their status", "Persist card positions to the backend via API calls", "Add smooth animations for card movement between columns"]),
    ("Build a markdown editor with preview", ["Create a split-pane layout with editor on left and preview on right", "Implement a markdown parser that converts text to HTML in real-time", "Add toolbar buttons for bold, italic, headers, and lists", "Implement syntax highlighting for code blocks within markdown", "Add export functionality to download the rendered HTML"]),
    ("Build a file upload service", ["Create a drag-and-drop file zone with visual feedback", "Implement chunked upload for large files with progress tracking", "Add file type validation and size limits on the client side", "Build a backend endpoint that saves files and returns URLs", "Add thumbnail generation for uploaded images"]),
    ("Build a data visualization dashboard", ["Set up a charting library and configure the rendering canvas", "Fetch time-series data from the API with proper date formatting", "Create interactive charts with tooltips and zoom functionality", "Add filter controls that update all charts simultaneously", "Implement auto-refresh with a configurable polling interval"]),
    ("Build a notification system", ["Design a notification schema with type, message, and read status", "Create an API endpoint to fetch unread notifications", "Implement real-time notification delivery via WebSocket", "Add a notification bell icon with unread count badge", "Build a notification panel that marks items as read on click"]),
]

P3_DATA = [
    ("How do I use useState?", "react-docs", "useState hook", "React Docs", "https://react.dev"),
    ("Explain useEffect cleanup", "react-docs", "useEffect cleanup", "React Docs", "https://react.dev"),
    ("How to create a custom hook?", "react-docs", "custom hooks", "React Docs", "https://react.dev"),
    ("What is React Context?", "react-docs", "React Context", "React Docs", "https://react.dev"),
    ("How does JSX work?", "react-docs", "JSX syntax", "React Docs", "https://react.dev"),
    ("Python list comprehension syntax", "python-docs", "list comprehension", "Python Docs", "https://docs.python.org"),
    ("How do decorators work?", "python-docs", "decorator pattern", "Python Docs", "https://docs.python.org"),
    ("Async await in Python", "python-docs", "async await", "Python Docs", "https://docs.python.org"),
    ("Explain context managers", "python-docs", "context manager", "Python Docs", "https://docs.python.org"),
    ("How do generators work?", "python-docs", "generator", "Python Docs", "https://docs.python.org"),
    ("How to use fetch API", "mdn-docs", "fetch API", "MDN Web Docs", "https://developer.mozilla.org"),
    ("CSS Grid layout guide", "mdn-docs", "CSS Grid", "MDN Web Docs", "https://developer.mozilla.org"),
    ("Flexbox complete guide", "mdn-docs", "Flexbox layout", "MDN Web Docs", "https://developer.mozilla.org"),
    ("JavaScript Promises", "mdn-docs", "Promises", "MDN Web Docs", "https://developer.mozilla.org"),
    ("localStorage API", "mdn-docs", "localStorage", "MDN Web Docs", "https://developer.mozilla.org"),
    ("Git workflow best practices", "github-docs", "Git workflow", "GitHub Docs", "https://docs.github.com"),
    ("How to write a PR template", "github-docs", "PR template", "GitHub Docs", "https://docs.github.com"),
    ("GitHub Actions CI setup", "github-docs", "actions CI", "GitHub Docs", "https://docs.github.com"),
    ("Repository setup guide", "github-docs", "repo setup", "GitHub Docs", "https://docs.github.com"),
    ("GitHub issue templates", "github-docs", "issue tracking", "GitHub Docs", "https://docs.github.com"),
]

P4_DATA = [
    ("React state management", [
        "useState returns an array with the current state and a setter function",
        "State updates trigger a re-render of the component and its children",
        "Functional updates like setCount(prev => prev + 1) prevent stale state"
    ], "React Docs", "https://react.dev", "2024"),
    ("CSS Grid layout", [
        "CSS Grid creates a two-dimensional layout system with rows and columns",
        "Grid template columns and rows define the track sizes using fr, px, or auto",
        "The gap property controls spacing between grid cells"
    ], "MDN Web Docs", "https://developer.mozilla.org", "2025"),
    ("JavaScript fetch API", [
        "Fetch returns a Promise that resolves to the Response object",
        "Response.json() parses the body as JSON and returns another Promise",
        "Always check response.ok before parsing to handle HTTP errors"
    ], "MDN Web Docs", "https://developer.mozilla.org", "2025"),
    ("Python decorators", [
        "Decorators are functions that wrap other functions to modify behavior",
        "functools.wraps preserves the original function's metadata",
        "Common uses: logging, timing, authentication, memoization"
    ], "Python Docs", "https://docs.python.org", "2024"),
    ("React useEffect", [
        "useEffect runs side effects after the component renders",
        "The cleanup function returned from useEffect runs on unmount",
        "The dependencies array controls when the effect re-runs"
    ], "React Docs", "https://react.dev", "2024"),
]

P5_DATA = [
    ("This component uses useState without a setter", "Missing setter in useState destructuring", "const [count, setCount] = useState(0) — you need both the value and the setter function"),
    ("The API key is hardcoded in the source", "Security vulnerability from exposed credentials", "Store API keys in environment variables using process.env.API_KEY or a .env file"),
    ("This for loop mutates the original array", "Mutation of original data causes side effects", "Use array.map() to create a new array instead of mutating the original with a for loop"),
    ("Error caught but not logged or re-thrown", "Silent error swallowing makes debugging impossible", "Always log errors with console.error and either re-throw or show a user-friendly message"),
    ("The CSS uses !important everywhere", "Overuse of !important breaks the cascade", "Use specific selectors instead of !important. Increase specificity by nesting or using classes"),
    ("Async function missing await on Promise call", "Missing await returns a Promise instead of the resolved value", "Add await before the async function call: const data = await fetchData()"),
    ("React component defined inside another component", "Nested component definitions cause remounting on every render", "Define components at module level, not inside other components or render functions"),
    ("Direct DOM manipulation in React", "Direct DOM manipulation conflicts with React's virtual DOM", "Use React state and refs instead of document.querySelector inside React components"),
    ("Array used as React key", "Using array index as key causes rendering bugs with dynamic lists", "Use a unique identifier like item.id as the key prop for list items"),
    ("Missing input validation on API endpoint", "Lack of validation causes database errors and security issues", "Validate input types, ranges, and formats before processing API requests"),
]


def generate_examples():
    rng = random.Random(42)
    data = []

    # P1 Reasoning
    for i in range(1000):
        q, a = rng.choice(P1_DATA)
        input_ids = [BOS] + t(q) + [14]
        target_ids = [4] + t(a) + [EOS]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:384], "mode": "plan", "domain": "reasoning"})

    # P2 Decomposition
    for i in range(1000):
        task, steps = rng.choice(P2_DATA)
        input_ids = [BOS] + t(f"Decompose: {task}") + [14]
        target_ids = [11]
        for step in steps:
            target_ids += t(step) + [14]
        target_ids = target_ids[:384] + [EOS]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids, "mode": "plan", "domain": "decomposition"})

    # P3 Dispatch
    for i in range(1000):
        q, bot_id, query, source, url = rng.choice(P3_DATA)
        dispatch = json.dumps({"bot_id": bot_id, "query": query})
        input_ids = [BOS] + t(q) + [14]
        target_ids = [7] + t(dispatch) + [8] + t(f"Found relevant documentation for {query} from {source}") + [9] + t(f"{source} {url} 2025") + [EOS]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:384], "mode": "plan", "domain": "dispatch"})

    # P4 Synthesis with citations
    for i in range(1500):
        title, snippets, source, url, year = rng.choice(P4_DATA)
        input_ids = [BOS] + t(f"Synthesize knowledge about {title}")
        for s in snippets:
            input_ids += [14] + t(s)
        input_ids = input_ids[:256] + [14]
        combined = " ".join(snippets[:2])
        target_ids = [5] + t(combined) + [9] + t(f"{source} {url} {year}") + [EOS]
        data.append({"input_ids": input_ids, "target_ids": target_ids[:384], "mode": "plan", "domain": "synthesis"})

    # P5 Self-correction
    for i in range(500):
        draft, error, fix = rng.choice(P5_DATA)
        input_ids = [BOS] + t(f"Fix: {draft}") + [14]
        target_ids = [6] + t(f"Error: {error}") + [5] + t(fix) + [EOS]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:384], "mode": "build", "domain": "correction"})

    rng.shuffle(data)
    return data


# ============================================================
# TRAINING
# ============================================================

class ValidDataset(torch.utils.data.Dataset):
    def __init__(self, data, max_len=512):
        self.samples = []
        for item in data:
            inp = item['input_ids'][:256]
            tgt = item['target_ids'][:384]
            combined = inp + tgt
            mask = [0]*len(inp) + [1]*len(tgt)
            if len(combined) > max_len:
                combined = combined[:max_len]
                mask = mask[:max_len]
            self.samples.append({'input_ids': combined, 'mask': mask, 'mode': item.get('mode', 'plan')})

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        return {'input_ids': torch.tensor(s['input_ids'], dtype=torch.long),
                'mask': torch.tensor(s['mask'], dtype=torch.float),
                'mode': s['mode']}


def collate(batch):
    ids = [b['input_ids'] for b in batch]
    masks = [b['mask'] for b in batch]
    modes = [b['mode'] for b in batch]
    max_len = max(len(i) for i in ids)
    padded_ids = torch.full((len(batch), max_len), PAD, dtype=torch.long)
    padded_masks = torch.zeros((len(batch), max_len), dtype=torch.float)
    for i, (id_, m) in enumerate(zip(ids, masks)):
        padded_ids[i, :len(id_)] = id_
        padded_masks[i, :len(m)] = torch.as_tensor(m, dtype=torch.float)
    return padded_ids, padded_masks, modes


def compute_loss_acc(logits, targets, mask):
    shift_logits = logits[:, :-1, :].contiguous()
    shift_targets = targets[:, 1:].contiguous()
    shift_mask = mask[:, 1:].contiguous()
    loss = F.cross_entropy(shift_logits.view(-1, shift_logits.size(-1)), shift_targets.view(-1), reduction='none')
    loss = loss.view(shift_logits.size(0), -1)
    masked_loss = (loss * shift_mask).sum() / (shift_mask.sum() + 1e-8)
    preds = shift_logits.argmax(dim=-1)
    correct = (preds == shift_targets) * shift_mask.bool()
    acc = correct.sum().float() / (shift_mask.sum() + 1e-8)
    return masked_loss, acc


def train(cfg, train_data, val_data, max_steps=10000):
    model = Keli10KModel(cfg)
    model.model.train()
    optimizer = torch.optim.AdamW(model.model.parameters(), lr=1e-4, weight_decay=0.01)

    train_ds = ValidDataset(train_data)
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=8, shuffle=True, collate_fn=collate)
    val_ds = ValidDataset(val_data)
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=8, shuffle=False, collate_fn=collate)

    best_val_loss = float('inf')
    best_step = 0
    step = 0
    epoch = 0
    results = []

    while step < max_steps:
        epoch += 1
        for input_ids, mask, modes in train_loader:
            if step >= max_steps:
                break
            input_ids = input_ids.to(device)
            mask = mask.to(device)
            targets = input_ids.clone()
            targets[targets == PAD] = -100
            is_build = all(m == 'build' for m in modes)
            logits, _ = model.model(input_ids, mode='build' if is_build else 'plan')
            loss, acc = compute_loss_acc(logits, targets, mask)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.model.parameters(), 1.0)
            optimizer.step()
            step += 1

            if step % 10 == 0:
                model.model.eval()
                val_losses, val_accs = [], []
                with torch.no_grad():
                    for vid, vm, vmodes in val_loader:
                        vid = vid.to(device)
                        vm = vm.to(device)
                        vt = vid.clone()
                        vt[vt == PAD] = -100
                        is_b = all(m == 'build' for m in vmodes)
                        vlogits, _ = model.model(vid, mode='build' if is_b else 'plan')
                        vl, va = compute_loss_acc(vlogits, vt, vm)
                        val_losses.append(vl.item())
                        val_accs.append(va.item())
                avg_vl = sum(val_losses)/len(val_losses)
                avg_va = sum(val_accs)/len(val_accs)
                model.model.train()

                results.append({'step': step, 'train_loss': loss.item(), 'val_loss': avg_vl, 'val_acc': avg_va})

                if avg_vl < best_val_loss:
                    best_val_loss = avg_vl
                    best_step = step
                    model.save(f'{CKPT_DIR}/keli_best.pt')

                if step % 100 == 0:
                    print(f"Step {step:5d} | Train: {loss.item():.4f} | Val: {avg_vl:.4f} | Acc: {avg_va*100:.1f}% | Best: {best_val_loss:.4f}@{best_step}")
                sys.stdout.flush()

    print(f"\nTraining completed: {step} steps, best val loss: {best_val_loss:.4f} at step {best_step}")
    return model, results, best_step


# ============================================================
# CONFIDENCE SCORING
# ============================================================

def get_confidence(logits):
    """Compute confidence score from logit distribution. Returns 0.0-1.0."""
    probs = F.softmax(logits, dim=-1)
    top_probs, top_indices = probs.topk(5, dim=-1)
    # Confidence = how much probability mass is in the top token
    # vs how spread out it is
    confidence = top_probs[..., 0]  # Top token probability
    # Uncertainty bonus: if second token is close, reduce confidence
    margin = top_probs[..., 0] - top_probs[..., 1] if top_probs.size(-1) > 1 else top_probs[..., 0]
    # Adjusted: high when top token is high AND margin is big
    adjusted = confidence * (0.5 + 0.5 * margin)
    return adjusted.mean().item()


# ============================================================
# TEST PROMPTS
# ============================================================

TEST_PROMPTS = [
    "How do I use useEffect?",
    "Build a todo app",
    "Fix this: const [todos] = useState()",
    "What is flexbox?",
    "Center a div",
    "Fetch API example",
    "React component with props",
    "SQL query for users table",
    "Explain closures",
    "Build a calculator",
]


def generate_text(model, prompt, max_tokens=256, temperature=0.7):
    """Generate text from prompt and return both text and confidence."""
    model.model.eval()
    input_ids = torch.tensor([[BOS] + t(prompt) + [14]]).to(device)
    generated = input_ids[0].tolist()
    confidences = []

    with torch.no_grad():
        for _ in range(max_tokens):
            logits, _ = model.model(input_ids, mode='plan')
            next_logits = logits[0, -1, :] / temperature
            probs = F.softmax(next_logits, dim=-1)
            top_prob, next_token = probs.topk(1)
            conf = get_confidence(logits[0, -1:, :].unsqueeze(0))
            confidences.append(conf)

            if next_token.item() == EOS:
                break

            generated.append(next_token.item())
            input_ids = torch.cat([input_ids, next_token.unsqueeze(0).unsqueeze(0)], dim=1)
            if input_ids.size(1) > 1024:
                break

    text = tok.decode(generated, skip_special=True)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    min_conf = min(confidences) if confidences else 0.0
    return text, {'avg_confidence': avg_conf, 'min_confidence': min_conf, 'num_tokens': len(confidences)}


def test_model(model):
    print("\n" + "="*60)
    print("FINAL TEST: 10 Prompts")
    print("="*60)
    results = []
    pass_count = 0

    for i, prompt in enumerate(TEST_PROMPTS):
        text, conf = generate_text(model, prompt)
        coherent = len(text) > 20 and not text.startswith('?') and text.count(' ') > 3
        if coherent:
            pass_count += 1
        results.append({
            'prompt': prompt,
            'output': text[:100] + '...' if len(text) > 100 else text,
            'coherent': coherent,
            'confidence': conf,
        })
        print(f"\nPrompt {i+1}: {prompt}")
        print(f"  Output: {text[:120]}{'...' if len(text) > 120 else ''}")
        print(f"  Coherent: {coherent} | Confidence: {conf['avg_confidence']:.3f} (min: {conf['min_confidence']:.3f})")
        sys.stdout.flush()

    return results, pass_count


# ============================================================
# MAIN
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true', help='Generate 5K examples')
    parser.add_argument('--train', action='store_true', help='Start training')
    parser.add_argument('--test', action='store_true', help='Run test prompts')
    parser.add_argument('--hours', type=float, default=24, help='Max training hours')
    parser.add_argument('--steps', type=int, default=10000, help='Max training steps')
    args = parser.parse_args()

    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(CKPT_DIR).mkdir(parents=True, exist_ok=True)

    cfg = SNCACfg()

    if args.generate:
        print("Generating 5,000 validation examples...")
        data = generate_examples()
        split = int(len(data) * 0.9)
        train_data = data[:split]
        val_data = data[split:]
        with open(f'{OUT_DIR}/train.jsonl', 'w') as f:
            for d in train_data:
                f.write(json.dumps(d) + '\n')
        with open(f'{OUT_DIR}/val.jsonl', 'w') as f:
            for d in val_data:
                f.write(json.dumps(d) + '\n')
        print(f"  Train: {len(train_data)} | Val: {len(val_data)}")
        print(f"  Saved to {OUT_DIR}/")

    if args.train:
        print(f"Loading data from {OUT_DIR}/...")
        train_data = [json.loads(l) for l in open(f'{OUT_DIR}/train.jsonl') if l.strip()]
        val_data = [json.loads(l) for l in open(f'{OUT_DIR}/val.jsonl') if l.strip()]
        print(f"  Train: {len(train_data)} | Val: {len(val_data)}")

        start_time = time.time()
        max_steps = args.steps
        timeout = args.hours * 3600

        steps_per_check = 10
        step_time_est = None

        model, results, best_step = train(cfg, train_data, val_data, max_steps=max_steps)
        elapsed = time.time() - start_time

        # Save results
        report = {
            'total_steps': len(results),
            'best_val_loss': min(r['val_loss'] for r in results),
            'best_step': best_step,
            'elapsed_hours': elapsed / 3600,
            'final_val_acc': results[-1]['val_acc'] if results else 0,
            'results': results,
            'pass': min(r['val_loss'] for r in results) < 3.0,
        }
        with open(f'{OUT_DIR}/training_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nTraining report saved to {OUT_DIR}/training_report.json")

    if args.test:
        print(f"Loading best model from {CKPT_DIR}/keli_best.pt...")
        model = Keli10KModel(cfg)
        model.load(f'{CKPT_DIR}/keli_best.pt')
        results, pass_count = test_model(model)

        # Pass criteria
        val_report = {}
        try:
            with open(f'{OUT_DIR}/training_report.json') as f:
                val_report = json.load(f)
        except:
            pass

        best_val_loss = val_report.get('best_val_loss', 999)
        val_acc = val_report.get('final_val_acc', 0)

        criteria = {
            'val_loss_below_3.0': best_val_loss < 3.0,
            'val_acc_exceeds_40%': val_acc > 0.40,
            'coherent_outputs_>=3': pass_count >= 3,
        }
        passed = sum(criteria.values()) >= 2

        final_report = {
            'model': 'keli_10k',
            'params': 21.32e6,
            'best_val_loss': best_val_loss,
            'val_accuracy': val_acc,
            'coherent_prompts': pass_count,
            'test_results': results,
            'criteria': criteria,
            'passed': passed,
            'verdict': 'PASS' if passed else 'FAIL',
            'recommendation': 'Scale to 50K examples, full curriculum training' if passed else 'Fix architecture or data quality',
        }
        with open(f'{OUT_DIR}/validation_report.json', 'w') as f:
            json.dump(final_report, f, indent=2)

        print("\n" + "="*60)
        print(f"VERDICT: {final_report['verdict']}")
        print("="*60)
        print(f"  Val Loss < 3.0: {criteria['val_loss_below_3.0']}")
        print(f"  Val Acc > 40%:  {criteria['val_acc_exceeds_40%']}")
        print(f"  Coherent >= 3:   {criteria['coherent_outputs_>=3']} ({pass_count}/10)")
        print(f"  Overall:         {final_report['verdict']}")
        print(f"  Recommended:     {final_report['recommendation']}")
        print(f"  Report:          {OUT_DIR}/validation_report.json")
        print()
        if passed:
            print("  PASSED validation. Proceed to scale training.")
        else:
            print("  FAILED validation. Diagnose and fix before scaling.")
        print("="*60)

    if not any([args.generate, args.train, args.test]):
        parser.print_help()


if __name__ == '__main__':
    main()
