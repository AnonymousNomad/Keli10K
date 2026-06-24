"""Step-by-step tutor engine for Keli."""
import sys, time

class TutorEngine:
    LESSONS = {
        'react hooks': {
            'title': 'React Hooks',
            'steps': [
                {
                    'prompt': 'Write the useState line with count and setCount initialized to 0:',
                    'answer': 'const [count, setCount] = useState(0);',
                    'hint': 'useState returns an array. Destructure it: const [value, setter] = useState(initial);',
                    'blueprint': '  State Node (count=0) ──→ Component\n  [useState hook]'
                },
                {
                    'prompt': 'Write the onClick handler to increment count:',
                    'answer': 'onClick={() => setCount(count + 1)}',
                    'hint': 'setCount accepts a new value. Use count + 1.',
                    'blueprint': '  Button ──→ onClick ──→ setCount(count+1) ──→ re-render'
                },
                {
                    'prompt': 'Write useEffect to log "mounted" on component mount:',
                    'answer': "useEffect(() => { console.log('mounted'); }, []);",
                    'hint': 'Empty dependency array = run once on mount.',
                    'blueprint': '  Component ──→ mount ──→ useEffect ──→ console.log'
                },
            ]
        },
        'python decorators': {
            'title': 'Python Decorators',
            'steps': [
                {
                    'prompt': 'Write a decorator function called timer that prints execution time:',
                    'answer': 'def timer(func):\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        print(f"Took {time.time()-start}s")\n        return result\n    return wrapper',
                    'hint': 'A decorator takes a function, defines a wrapper, calls the original, returns the wrapper.',
                    'blueprint': '  func ──→ timer(func) ──→ wrapper ──→ call func + timing'
                },
                {
                    'prompt': 'Use @ syntax to apply the timer decorator:',
                    'answer': '@timer\ndef my_func():\n    time.sleep(1)',
                    'hint': '@decorator_name goes right above the function definition.',
                    'blueprint': '  @timer\n  def my_func()\n  ║\n  my_func = timer(my_func)'
                },
            ]
        },
    }

    def __init__(self):
        self.current_lesson = None
        self.current_step = 0
        self.total_steps = 0

    def list_lessons(self):
        sys.stdout.write('\033[1;96mAvailable Lessons:\033[0m\n')
        for name, lesson in self.LESSONS.items():
            sys.stdout.write(f'  \033[93m•\033[0m {lesson["title"]} (\033[94m{len(lesson["steps"])} steps\033[0m)\n')
        sys.stdout.write('\n')

    def start_lesson(self, lesson_key):
        lesson_key = lesson_key.lower()
        matched = None
        for key in self.LESSONS:
            if lesson_key in key.lower() or lesson_key in self.LESSONS[key]['title'].lower():
                matched = key
                break
        if not matched:
            return f'Lesson "{lesson_key}" not found. Try: react hooks, python decorators'

        lesson = self.LESSONS[matched]
        self.current_lesson = matched
        self.current_step = 0
        self.total_steps = len(lesson['steps'])
        return f'\033[1;96mLesson 1/{self.total_steps}: {lesson["title"]}\033[0m'

    def get_step(self):
        if not self.current_lesson:
            return None
        lesson = self.LESSONS[self.current_lesson]
        if self.current_step >= self.total_steps:
            return None
        return lesson['steps'][self.current_step]

    def advance(self):
        step = self.get_step()
        if step:
            self.current_step += 1
        return self.current_step < self.total_steps

    def render_step(self):
        step = self.get_step()
        if not step:
            msg = '\033[92m✓ Lesson complete!\033[0m'
            sys.stdout.write(f'\n  \033[1;96m[◢◣ Keli]:\033[0m {msg}\n')
            sys.stdout.write(f'  Type \033[93mcertify\033[0m to get your completion badge.\n\n')
            sys.stdout.flush()
            return False

        num = self.current_step + 1
        lesson = self.LESSONS[self.current_lesson]
        sys.stdout.write(f'\n\033[96m┌─[{lesson["title"]}]─[Step {num}/{self.total_steps}]─\033[0m\n')
        sys.stdout.write(f'\033[96m│\033[0m\n')
        sys.stdout.write(f'  \033[1;93m[◢◣ Keli]:\033[0m {step["prompt"]}\n')
        if step.get('blueprint'):
            sys.stdout.write(f'\n  \033[90m[Blueprint]\033[0m \033[2;36m{step["blueprint"]}\033[0m\n')
        sys.stdout.write(f'\n  \033[2;96mType the code, or \033[93mhint\033[0m\033[2;96m, \033[93mskip\033[0m\033[2;96m:\033[0m\n')
        sys.stdout.write(f'\033[36mkeli@sovereign:tutor$\033[0m ')
        sys.stdout.flush()
        return True

    def check_answer(self, user_input):
        step = self.get_step()
        if not step:
            return True, ''
        expected = step['answer'].strip()
        user_clean = user_input.strip().replace('\\s+', ' ').replace('"', "'")
        expected_clean = expected.replace('"', "'")
        is_correct = user_clean in expected_clean or expected_clean in user_clean
        if is_correct:
            msg = '\033[92m✓ Correct.\033[0m'
            self.current_step += 1
        else:
            msg = f'\033[93m✗ Not quite. Expected:\033[0m\n  {expected}'
        return is_correct, msg

    def get_hint(self):
        step = self.get_step()
        return step['hint'] if step else ''

    def generate_certificate(self):
        if self.current_lesson and self.current_step >= self.total_steps:
            lesson = self.LESSONS[self.current_lesson]
            cert = (
                f'\033[96m┌─────────────────────────────────────────┐\033[0m\n'
                f'\033[96m│\033[0m  \033[93mCERTIFICATE OF COMPLETION\033[0m            \033[96m│\033[0m\n'
                f'\033[96m│\033[0m                                         \033[96m│\033[0m\n'
                f'\033[96m│\033[0m  \033[1;96m{lesson["title"]:<37}\033[0m\033[96m│\033[0m\n'
                f'\033[96m│\033[0m  Keli Sovereign IDE                     \033[96m│\033[0m\n'
                f'\033[96m│\033[0m  10,000 Nanobots verified                \033[96m│\033[0m\n'
                f'\033[96m│\033[0m  Date: {time.strftime("%Y-%m-%d")}                   \033[96m│\033[0m\n'
                f'\033[96m└─────────────────────────────────────────┘\033[0m\n'
            )
            return cert
        return '\033[33mComplete the lesson first.\033[0m\n'
