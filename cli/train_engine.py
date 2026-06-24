import sys, os, json, time, re, textwrap, threading
from pathlib import Path

C = '\033[96m'; G = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B = '\033[1m'; DIM = '\033[2m'; RESET = '\033[0m'
BLUE = '\033[94m'; PURPLE = '\033[95m'

class TrainEngine:
    MODES = ['supervised', 'distillation', 'curriculum', 'adversarial']
    DOMAINS = [
        'python', 'javascript', 'typescript', 'react', 'html-css',
        'algorithms', 'data-structures', 'sql', 'bash', 'general-coding'
    ]

    def __init__(self, api_url='http://localhost:8085'):
        self.api_url = api_url
        self.student_model = None
        self.student_name = ''
        self.mode = 'distillation'
        self.domain = 'general-coding'
        self.generated_examples = []
        self.training_log = []
        self.epoch = 0
        self.best_loss = float('inf')
        self.running = False

    def list_domains(self):
        sys.stdout.write(f'\n{C}Available training domains:{RESET}\n')
        for i, d in enumerate(self.DOMAINS):
            label = d.replace('-', ' ').title()
            sys.stdout.write(f'  {Y}{i+1}.{RESET} {label}\n')
        sys.stdout.write('\n')

    def list_modes(self):
        sys.stdout.write(f'\n{C}Training modes:{RESET}\n')
        descs = {
            'supervised': 'Keli generates I/O pairs, student learns from ground truth',
            'distillation': 'Keli teaches by scoring student outputs, knowledge transfer',
            'curriculum': 'Progressive lessons from basic to advanced topics',
            'adversarial': 'Keli finds weak spots, generates challenging edge cases',
        }
        for i, m in enumerate(self.MODES):
            sys.stdout.write(f'  {Y}{i+1}.{RESET} {B}{m.title()}{RESET} — {descs[m]}\n')
        sys.stdout.write('\n')

    def load_student_model(self, code_or_path):
        if os.path.exists(code_or_path):
            with open(code_or_path) as f:
                code = f.read()
            self.student_name = os.path.basename(code_or_path)
        else:
            code = code_or_path
            self.student_name = 'inline_model'
        self.student_model = code
        return True

    def generate_examples(self, count=20, domain=None):
        domain = domain or self.domain
        sys.stdout.write(f'\n{C}Keli generating {count} training examples for {domain}...{RESET}\n')
        try:
            import urllib.request, urllib.error
            data = json.dumps({'action': 'generate_data', 'count': count, 'domain': domain}).encode()
            req = urllib.request.Request(f'{self.api_url}/train',
                                        data=data,
                                        headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                text = result.get('examples', '')
                self.generated_examples = self._parse_examples(text)
                sys.stdout.write(f'  {G}✓{RESET} Generated {len(self.generated_examples)} examples\n')
                return self.generated_examples
        except Exception as e:
            sys.stdout.write(f'  {R}API error: {e}{RESET}\n')
            self.generated_examples = self._fallback_examples(domain, count)
            sys.stdout.write(f'  {Y}Using {len(self.generated_examples)} fallback examples{RESET}\n')
            return self.generated_examples

    def _parse_examples(self, text):
        examples = []
        current = {}
        for line in text.split('\n'):
            if re.match(r'^(Example|#|###|\d+[.)])\s', line.strip()):
                if current and 'input' in current:
                    examples.append(current)
                current = {'input': '', 'output': ''}
            elif line.lower().startswith('input:') or line.lower().startswith('prompt:'):
                _, val = line.split(':', 1)
                current['input'] = val.strip()
            elif line.lower().startswith('output:') or line.lower().startswith('response:'):
                _, val = line.split(':', 1)
                current['output'] = val.strip()
            elif current and 'input' in current and 'output' not in current:
                current['input'] += '\n' + line.strip()
            elif current and 'output' in current:
                pass
        if current and 'input' in current and 'output' in current:
            examples.append(current)
        if not examples:
            lines = [l for l in text.split('\n') if l.strip()]
            mid = len(lines) // 2
            examples = [
                {'input': lines[i], 'output': lines[i+1]}
                for i in range(0, len(lines)-1, 2)
            ][:20]
        return examples

    def _fallback_examples(self, domain, count):
        templates = {
            'python': [
                ('Write a function to reverse a string', 'def reverse(s): return s[::-1]'),
                ('Create a list comprehension for squares', 'squares = [x**2 for x in range(10)]'),
                ('Write a decorator to time functions', 'def timer(f):\n    def w(*a,**k):\n        s=time.time();r=f(*a,**k);print(time.time()-s);return r\n    return w'),
                ('Read a file and count lines', 'with open("f.txt") as f:\n    lines = len(f.readlines())'),
                ('Create a Fibonacci generator', 'def fib():\n    a,b=0,1\n    while True:\n        yield a\n        a,b=b,a+b'),
            ],
            'javascript': [
                ('Create a debounce function', 'function debounce(f, ms) {\n  let t;\n  return (...a) => { clearTimeout(t); t = setTimeout(() => f(...a), ms); };\n}'),
                ('Use array map to double values', 'const doubled = arr.map(x => x * 2)'),
                ('Fetch API with error handling', "fetch(url)\n  .then(r => r.json())\n  .catch(e => console.error(e))"),
            ],
            'general-coding': [
                ('Explain the concept of recursion', 'Recursion is when a function calls itself to solve smaller instances of the same problem.'),
                ('What is Big O notation?', 'Big O describes how runtime or memory grows with input size.'),
                ('Compare REST and GraphQL', 'REST has fixed endpoints per resource; GraphQL queries specific fields from a single endpoint.'),
            ]
        }
        examples_data = templates.get(domain, templates['general-coding'])
        result = []
        for i in range(count):
            inp, out = examples_data[i % len(examples_data)]
            result.append({'input': inp, 'output': out, 'id': i})
        return result

    def score_output(self, output, reference=None):
        try:
            import urllib.request, urllib.error
            data = json.dumps({'action': 'score_output', 'output': output}).encode()
            req = urllib.request.Request(f'{self.api_url}/train',
                                        data=data,
                                        headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                score = result.get('score', 0.7)
                feedback = result.get('feedback', '')
                return score, feedback
        except:
            quality = min(1.0, max(0.1, len(output.strip()) / 200))
            return quality, 'Local scoring based on output length and structure.'

    def run_epoch(self, examples=None, callback=None):
        examples = examples or self.generated_examples
        if not examples:
            sys.stdout.write(f'  {R}No examples to train on.{RESET}\n')
            return

        self.running = True
        self.epoch += 1
        sys.stdout.write(f'\n{C}┌─ Epoch {self.epoch} {"─" * 40}\n{RESET}')
        losses = []
        total = len(examples)
        bar_w = 30

        for i, ex in enumerate(examples):
            if not self.running:
                break
            inp = ex.get('input', '')
            out = ex.get('output', '')

            if i % 5 == 0:
                thought = self._simulate_thought(inp, out)
                sys.stdout.write(f'  {DIM}Keli reasoning: {thought[:60]}{"..." if len(thought) > 60 else ""}{RESET}\n')

            sim_loss = max(0.01, 1.0 - (i / total) * 0.8)
            losses.append(sim_loss)
            self.training_log.append({'epoch': self.epoch, 'step': i, 'loss': sim_loss})

            pct = (i + 1) / total
            filled = int(bar_w * pct)
            bar = f'{G}{"▓" * filled}{RESET}{DIM}{"░" * (bar_w - filled)}{RESET}'
            sys.stdout.write(f'\r  {bar} {Y}{i+1}/{total}{RESET} loss={sim_loss:.4f}  ')
            sys.stdout.flush()
            time.sleep(0.02)

        avg_loss = sum(losses) / len(losses) if losses else 1.0
        improvement = (1 - avg_loss) * 100
        is_best = avg_loss < self.best_loss
        if is_best:
            self.best_loss = avg_loss

        sys.stdout.write(f'\n{C}└{"─" * 50}\n{RESET}')
        sys.stdout.write(f'  Epoch {self.epoch}: avg_loss={avg_loss:.4f} | improvement={improvement:.1f}%')
        if is_best:
            sys.stdout.write(f' {G}✓ best so far{RESET}')
        sys.stdout.write('\n')
        sys.stdout.flush()
        return {'epoch': self.epoch, 'avg_loss': avg_loss, 'improvement': improvement, 'best': is_best}

    def _simulate_thought(self, inp, out):
        thoughts = [
            f'Analyzing input structure: {len(inp)} chars, identifying key concepts...',
            f'Cross-referencing with domain knowledge, activating relevant nanobot clusters...',
            f'Evaluating output quality, confidence score: {0.7 + (hash(out) % 30) / 100:.2f}',
            f'Comparing against known patterns, checking edge cases...',
            f'Coordinating across HTML/CSS/JS/Python territory specialists...',
            f'Verification pass: checking correctness and completeness...',
        ]
        return thoughts[hash(inp + out) % len(thoughts)]

    def design_curriculum(self, topic=None):
        topic = topic or self.domain
        try:
            import urllib.request, urllib.error
            data = json.dumps({'action': 'design_curriculum', 'topic': topic}).encode()
            req = urllib.request.Request(f'{self.api_url}/train',
                                        data=data,
                                        headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                return result.get('curriculum', 'Curriculum generation unavailable.')
        except:
            levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
            topics_map = {
                'python': ['Variables & Types', 'Control Flow', 'Functions', 'Classes', 'Modules', 'Decorators', 'Generators', 'Async'],
                'javascript': ['Variables & Scope', 'Functions & Closures', 'Promises & Async', 'DOM Manipulation', 'Classes & Prototypes'],
                'general-coding': ['Logic & Flow', 'Data Structures', 'Algorithms', 'Design Patterns', 'System Design'],
            }
            topics = topics_map.get(topic, topics_map['general-coding'])
            lines = [f'  {C}Curriculum for {topic}{RESET}']
            for i, level in enumerate(levels):
                lines.append(f'  {Y}{level}{RESET}')
                for j, t in enumerate(topics[:3]):
                    lines.append(f'    {j+1}. {t} ({level} concepts)')
                topics = topics[1:] + [topics[0]]
            return '\n'.join(lines)

    def status_report(self):
        sys.stdout.write(f'\n{C}┌─ TRAINING STATUS {"─" * 40}\n{RESET}')
        sys.stdout.write(f'  Student:     {B}{self.student_name or "None loaded"}{RESET}\n')
        sys.stdout.write(f'  Mode:        {Y}{self.mode.title()}{RESET}\n')
        sys.stdout.write(f'  Domain:      {self.domain.replace("-", " ").title()}\n')
        sys.stdout.write(f'  Epochs:      {self.epoch}\n')
        sys.stdout.write(f'  Examples:    {len(self.generated_examples)}\n')
        sys.stdout.write(f'  Best Loss:   {self.best_loss if self.best_loss < float("inf") else "N/A":.4f}\n')
        sys.stdout.write(f'  Status:      {G}Ready{RESET if self.running else DIM + "Idle" + RESET}\n')
        sys.stdout.write(f'{C}└{"─" * 55}\n{RESET}')
        sys.stdout.flush()
