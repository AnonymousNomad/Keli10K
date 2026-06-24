"""Typewriter response renderer with syntax highlighting."""
import sys, time, re, json, urllib.request, urllib.error

class ResponseRenderer:
    SYNTAX_MAP = {
        r'(def |class |import |from |return|if |elif |else:|for |while |try:|except|with |async |await )': '\033[1;94m',
        r'("[^"]*"|\'[^\']*\')': '\033[92m',
        r'(#.*)': '\033[90m',
        r'(\b\d+\.?\d*\b)': '\033[93m',
        r'(```[\s\S]*?```)': None,
    }

    LANG_MAP = {
        'py': '\033[93mPython\033[0m', 'js': '\033[92mJavaScript\033[0m',
        'ts': '\033[94mTypeScript\033[0m', 'css': '\033[95mCSS\033[0m',
        'html': '\033[91mHTML\033[0m', 'json': '\033[93mJSON\033[0m',
        'bash': '\033[90mBash\033[0m'
    }

    def __init__(self, api_url='http://localhost:8080'):
        self.api_url = api_url

    def typewriter(self, text, delay=0.015):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\n')

    def highlight(self, text):
        lang_match = re.match(r'```(\w+)', text)
        if lang_match:
            lang = lang_match.group(1)
            label = self.LANG_MAP.get(lang, f'\033[96m{lang}\033[0m')
            return f'  [{label}]'
        return text

    def render_keli_response(self, lines, typewriter_delay=0.01):
        sys.stdout.write('\033[1;93m[◢◣ Keli]:\033[0m ')
        sys.stdout.flush()
        in_code = False
        code_lang = ''
        for i, line in enumerate(lines):
            if line.startswith('```'):
                if in_code:
                    in_code = False
                    sys.stdout.write('\033[0m\n')
                else:
                    in_code = True
                    code_lang = line[3:].strip()
                    hl = self.LANG_MAP.get(code_lang, f'\033[96m{code_lang}\033[0m')
                    sys.stdout.write(f'\n  \033[90m┌─[{hl}]─\033[0m\n')
                sys.stdout.flush()
                continue
            if in_code:
                sys.stdout.write(f'  \033[90m│\033[0m {line}\n')
            elif line.startswith('[') and ']' in line:
                sys.stdout.write(f'\033[2;36m{line}\033[0m\n')
            else:
                for char in line:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(typewriter_delay)
                sys.stdout.write('\n')
            sys.stdout.flush()
        if in_code:
            sys.stdout.write(f'  \033[90m└───────\033[0m\n\033[0m')
        sys.stdout.write('\n')
        sys.stdout.flush()

    def call_api(self, text, mode='plan'):
        try:
            data = json.dumps({'text': text, 'mode': mode}).encode()
            req = urllib.request.Request(f'{self.api_url}/chat', data=data,
                                        headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())['response']
        except Exception:
            return None

    def render_build_output(self, files):
        sys.stdout.write('\n\033[1;96m[◢◣ Keli]:\033[0m \033[92mDone.\033[0m Here\'s your project:\n')
        for name, size in files:
            sys.stdout.write(f'  \033[93m📄\033[0m {name}  (\033[94m{size})\033[0m\n')
        sys.stdout.write('\n')
        sys.stdout.flush()
