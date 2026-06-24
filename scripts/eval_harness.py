import json
import re
import sys
import torch
import math
from pathlib import Path

PAD, EOS, BOS, PLAN, EXEC, REFLECT, TOOL_CALL, TOOL_RESULT, CITE, UNSURE, DECOMP = \
    0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11


def _decode(ids, vocab_size=8192):
    first_ascii = 32
    chars = []
    for i in ids:
        if i in (PAD, EOS, BOS):
            continue
        if i == PLAN:
            chars.append('<PLAN>')
        elif i == EXEC:
            chars.append('<EXEC>')
        elif i == REFLECT:
            chars.append('<REFLECTION>')
        elif i == TOOL_CALL:
            chars.append('<TOOL_CALL>')
        elif i == TOOL_RESULT:
            chars.append('<TOOL_RESULT>')
        elif i == CITE:
            chars.append('<CITE>')
        elif i == UNSURE:
            chars.append('<UNSURE>')
        elif i == DECOMP:
            chars.append('<DECOMP>')
        elif first_ascii <= i < 128:
            chars.append(chr(i))
        elif i >= 128:
            m = (i - 128) % 95 + 32
            chars.append(chr(m))
        else:
            chars.append('?')
    return ''.join(chars)


def _has_token(ids, token_id):
    return token_id in ids


def _count_citations(text):
    return len(re.findall(r'\[([^\]]+)\]\(https?://[^\)]+\s+\d{4}\)', text))


PLAN_PROMPTS = [
    "How do I manage state in React?",
    "Explain CSS Grid layout",
    "What is the Fetch API?",
    "How do Python list comprehensions work?",
    "Create a React component with useState",
    "How to use useEffect for data fetching",
    "Explain async/await in JavaScript",
    "What are Python decorators?",
    "How does localStorage work?",
    "Build a responsive navbar with CSS Flexbox",
    "How to handle forms in React?",
    "What is the Context API?",
    "Explain Promise chaining",
    "How to sort arrays in JavaScript?",
    "What are CSS custom properties?",
    "How does binary search work?",
    "Explain React useEffect cleanup",
    "What is the difference between var let and const?",
    "How to use SQLite in Python?",
    "What are React keys and why are they important?",
    "How to implement drag and drop?",
    "Explain CSS animations",
    "What are Python generators?",
    "How does the JavaScript event loop work?",
    "Create a custom React hook for form handling",
    "How to deploy a Node.js app?",
    "Explain REST API best practices",
    "What is JSX syntax?",
    "How to use CSS media queries?",
    "Explain React useRef hook",
    "How to handle errors in async functions?",
    "What are Python context managers?",
    "How does CSS specificity work?",
    "Explain React useMemo hook",
    "How to implement pagination in an API?",
    "What is the difference between grid and flexbox?",
    "How to use environment variables in Node.js?",
    "Explain JavaScript closures",
    "What are web workers?",
    "How to optimize React re-renders?",
    "Create a Python function to read a CSV file",
    "How to use CSS transitions?",
    "Explain React useCallback",
    "What is the virtual DOM?",
    "How to implement authentication in Express?",
    "What are Python lambda functions?",
    "How to use the HTML Canvas API?",
    "Explain JavaScript prototypal inheritance",
    "How to test React components?",
    "What are WebSockets and how do they work?",
    "How to create a dark mode toggle?",
    "Explain React portals",
    "What is the CSS box model?",
    "How to use Python multiprocessing?",
    "Explain JavaScript Proxy",
    "What are React error boundaries?",
    "How to use CSS variables for theming?",
    "Explain the JavaScript module system",
    "How to build a search bar with autocomplete?",
    "What is the Intersection Observer API?",
    "How to use Python pathlib for file operations?",
    "Explain React refs with forwardRef",
    "What is Tailwind CSS?",
    "How to implement infinite scrolling?",
    "Explain JavaScript destructuring",
    "What are React fragments?",
    "How to use Python virtual environments?",
    "Explain SQL injection prevention",
    "What is the CSS Flexbox vs Grid decision?",
    "How to create a custom error class in Python?",
    "Explain JavaScript spread operator",
    "How to use the Web Storage API?",
    "What are React compound components?",
    "How to implement debouncing in JavaScript?",
    "Explain Python's __init__ method",
    "What is the Shadow DOM?",
    "How to create accessible forms?",
    "Explain React Strict Mode",
    "What are CSS pseudo-classes?",
    "How to handle file uploads in Node.js?",
    "Explain JavaScript currying",
    "How to implement a pub/sub pattern?",
    "What are React higher-order components?",
    "How to use Python list slicing?",
    "Explain the browser rendering pipeline",
    "What is the CSS contain property?",
    "How to create a React portal for modals?",
    "Explain JavaScript Symbol type",
    "How to implement rate limiting in Express?",
    "What are React suspense boundaries?",
    "How to use CSS aspect-ratio?",
    "Explain JavaScript generator functions",
    "What is the Python collections module?",
    "How to create a CLI tool with Python argparse?",
    "Explain React controlled vs uncontrolled inputs",
    "How to use CSS scroll snap?",
    "What are JavaScript typed arrays?",
    "How to implement OAuth 2.0 in a web app?",
    "Explain the React reconciliation algorithm",
    "What is the Python functools module?",
    "How to create toast notifications in React?",
    "Explain CSS container queries",
    "How to use Python's asyncio for concurrent tasks?",
    "What are React server components?",
]


BUILD_TASKS = [
    {"task": "Create a React dashboard with a chart", "territory": "frontend"},
    {"task": "Build a contact form with validation", "territory": "frontend"},
    {"task": "Create a responsive navigation bar", "territory": "frontend"},
    {"task": "Build a modal dialog component", "territory": "frontend"},
    {"task": "Create a data table with sorting", "territory": "frontend"},
    {"task": "Build a card layout grid", "territory": "frontend"},
    {"task": "Create a dark mode toggle", "territory": "frontend"},
    {"task": "Build a file upload form", "territory": "frontend"},
    {"task": "Create an image carousel", "territory": "frontend"},
    {"task": "Build a progress bar component", "territory": "frontend"},
    {"task": "Implement a REST API with Express", "territory": "backend"},
    {"task": "Build a user authentication system", "territory": "backend"},
    {"task": "Create a WebSocket server", "territory": "backend"},
    {"task": "Implement a rate limiter middleware", "territory": "backend"},
    {"task": "Build a file server in Node.js", "territory": "backend"},
    {"task": "Create a logging middleware", "territory": "backend"},
    {"task": "Implement a caching layer", "territory": "backend"},
    {"task": "Build a job queue system", "territory": "backend"},
    {"task": "Create a search API endpoint", "territory": "backend"},
    {"task": "Implement request validation middleware", "territory": "backend"},
    {"task": "Write a Python data pipeline", "territory": "data"},
    {"task": "Create a CSV parser", "territory": "data"},
    {"task": "Build a data transformation script", "territory": "data"},
    {"task": "Implement a database migration", "territory": "data"},
    {"task": "Create a data validation pipeline", "territory": "data"},
    {"task": "Build an ETL process", "territory": "data"},
    {"task": "Write a report generator", "territory": "data"},
    {"task": "Create a data aggregation query", "territory": "data"},
    {"task": "Implement a data export function", "territory": "data"},
    {"task": "Build a real time data stream processor", "territory": "data"},
    {"task": "Write a Dockerfile for a Node app", "territory": "devops"},
    {"task": "Create a CI pipeline config", "territory": "devops"},
    {"task": "Write deployment scripts", "territory": "devops"},
    {"task": "Configure nginx reverse proxy", "territory": "devops"},
    {"task": "Create a kubernetes deployment", "territory": "devops"},
    {"task": "Write a monitoring script", "territory": "devops"},
    {"task": "Create a backup automation", "territory": "devops"},
    {"task": "Write environment setup script", "territory": "devops"},
    {"task": "Configure SSL certificate renewal", "territory": "devops"},
    {"task": "Create a health check endpoint", "territory": "devops"},
    {"task": "Make a React dashboard with real time data", "territory": "frontend"},
    {"task": "Build a microservice in Node.js", "territory": "backend"},
    {"task": "Create a data warehouse pipeline", "territory": "data"},
    {"task": "Write terraform configs", "territory": "devops"},
    {"task": "Build a chat UI component", "territory": "frontend"},
    {"task": "Create a REST client library", "territory": "backend"},
    {"task": "Implement feature flags system", "territory": "backend"},
    {"task": "Build a notification service", "territory": "backend"},
    {"task": "Create a React form with validation", "territory": "frontend"},
    {"task": "Deploy a Python app with gunicorn", "territory": "devops"},
]


class EvalHarness:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.results = []

    def _gen(self, prompt, mode='plan', territory_idx=None, max_new=128):
        input_ids = self.tokenizer.encode(prompt, bos=True, eos=False)
        input_tensor = torch.tensor([input_ids])
        kwargs = {'mode': mode}
        if mode == 'build':
            kwargs['territory_idx'] = territory_idx
        out = self.model.generate(input_tensor, max_new=max_new, temperature=0.5, **kwargs)
        return _decode(out[0].tolist())

    def test_plan_mode_tags(self):
        n_test = min(len(PLAN_PROMPTS), 100)
        passed = 0
        details = []
        for i, prompt in enumerate(PLAN_PROMPTS[:n_test]):
            output = self._gen(prompt, mode='plan')
            has_plan = '<PLAN>' in output
            has_exec = '<EXEC>' in output
            has_tool = '<TOOL_CALL>' in output
            has_refl = '<REFLECTION>' in output
            any_tag = has_plan or has_exec or has_tool or has_refl

            if any_tag:
                passed += 1
            details.append({
                'prompt': prompt,
                'tags_found': [t for t, f in [('<PLAN>', has_plan), ('<EXEC>', has_exec),
                                              ('<TOOL_CALL>', has_tool), ('<REFLECTION>', has_refl)] if f],
                'output_preview': output[:60],
            })
        self.results.append({
            'test': 'plan_mode_tags',
            'passed': passed,
            'total': n_test,
            'score': passed / max(n_test, 1),
            'details': details,
        })
        return passed / max(n_test, 1)

    def test_build_mode(self):
        n_test = min(len(BUILD_TASKS), 50)
        passed = 0
        territory_hits = {}
        details = []
        territories = ['frontend', 'backend', 'data', 'devops']
        for i, bt in enumerate(BUILD_TASKS[:n_test]):
            t_idx = territories.index(bt['territory'])
            output = self._gen(bt['task'], mode='build', territory_idx=t_idx)
            has_code = bool(re.search(r'(function|const|let|var|def |class |import|export|<[a-z])', output))
            has_territory = bt['territory'] in output.lower()

            if has_code:
                passed += 1
                territory_hits[bt['territory']] = territory_hits.get(bt['territory'], 0) + 1
            details.append({
                'task': bt['task'],
                'territory': bt['territory'],
                'has_code': has_code,
                'has_territory': has_territory,
                'output_preview': output[:60],
            })
        self.results.append({
            'test': 'build_mode',
            'passed': passed,
            'total': n_test,
            'score': passed / max(n_test, 1),
            'territory_hits': territory_hits,
            'details': details,
        })
        return passed / max(n_test, 1)

    def test_citation_recall(self):
        n_test = min(len(PLAN_PROMPTS), 100)
        cited = 0
        details = []
        for i, prompt in enumerate(PLAN_PROMPTS[:n_test]):
            output = self._gen(prompt, mode='plan')
            n_cite = _count_citations(output)
            has_citation = n_cite > 0
            if has_citation:
                cited += 1
            details.append({
                'prompt': prompt,
                'has_citation': has_citation,
                'n_citations': n_cite,
                'output_preview': output[:60],
            })
        self.results.append({
            'test': 'citation_recall',
            'passed': cited,
            'total': n_test,
            'score': cited / max(n_test, 1),
            'details': details,
        })
        return cited / max(n_test, 1)

    def test_unsure_compliance(self):
        offline_prompts = [
            "What is the capital of Atlantis?",
            "Explain quantum consciousness",
            "Who built the pyramids of Mars?",
            "What happened in the year 5000 BC exactly?",
            "Translate this into Klingon",
            "What is the meaning of life according to aliens?",
            "How do I time travel?",
            "Explain the plot of a show that was never made",
            "Who invented the perpetual motion machine?",
            "What is the chemical formula for love?",
        ]
        passed = 0
        details = []
        for prompt in offline_prompts:
            output = self._gen(prompt, mode='plan')
            has_unsure = '<UNSURE>' in output
            if has_unsure:
                passed += 1
            details.append({
                'prompt': prompt,
                'has_unsure': has_unsure,
                'output_preview': output[:60],
            })
        self.results.append({
            'test': 'unsure_compliance',
            'passed': passed,
            'total': len(offline_prompts),
            'score': passed / max(len(offline_prompts), 1),
            'details': details,
        })
        return passed / max(len(offline_prompts), 1)

    def run_all(self):
        print("=== Keli10K Evaluation Harness ===\n")
        tests = [
            ('plan_mode_tags', self.test_plan_mode_tags),
            ('build_mode', self.test_build_mode),
            ('citation_recall', self.test_citation_recall),
            ('unsure_compliance', self.test_unsure_compliance),
        ]
        for name, fn in tests:
            print(f"Test: {name} ...")
            score = fn()
            status = 'PASS' if score >= 0.5 else 'FAIL'
            print(f"  Score: {score:.2%} [{status}]\n")

        overall = sum(r['score'] for r in self.results) / max(len(self.results), 1)
        self.results.append({
            'test': 'overall',
            'score': overall,
            'status': 'PASS' if overall >= 0.5 else 'FAIL',
        })
        print(f"Overall: {overall:.2%} [{'PASS' if overall >= 0.5 else 'FAIL'}]")

        report_path = Path('eval_report.json')
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Report saved to {report_path}")
        return self.results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', default='checkpoints/swarm_best.pt')
    parser.add_argument('--model-type', default='keli')
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from snca_config import SNCACfg
    from snca_tokenizer import SNCATokenizer
    cfg = SNCACfg()
    tok = SNCATokenizer()

    if args.model_type == 'keli':
        from keli_10k import Keli10KModel
        model = Keli10KModel(cfg)
    else:
        from snca_model import SNCAModel
        model = SNCAModel(cfg)

    ckpt_path = Path(args.checkpoint)
    if ckpt_path.exists():
        model.load(str(ckpt_path))
        print(f"Loaded checkpoint: {args.checkpoint}")
    else:
        print(f"Checkpoint not found: {args.checkpoint}")
        print("Running evaluation with untrained model (random outputs)")

    harness = EvalHarness(model, tok)
    harness.run_all()


if __name__ == '__main__':
    main()
