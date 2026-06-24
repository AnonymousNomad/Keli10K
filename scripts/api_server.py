#!/usr/bin/env python3
import sys, os, json, io, zipfile, tempfile, shutil, re, html as html_mod, time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HOST = '0.0.0.0'
PORT = 8085
CHECKPOINT_DIR = Path(__file__).parent.parent / 'checkpoints'

model = None
tok = None
generate_fn = None

def try_load_model():
    global model, tok, generate_fn
    try:
        from snca_config import SNCACfg
        from snca_tokenizer import SNCATokenizer
        from keli_10k import Keli10KModel
        from scripts.confidence import generate_with_confidence as _gen

        generate_fn = _gen
        tok = SNCATokenizer()
        best = CHECKPOINT_DIR / 'keli_best.pt'
        latest = CHECKPOINT_DIR / 'keli_final.pt'
        ckpt = latest if latest.exists() else (best if best.exists() else None)
        if ckpt:
            cfg = SNCACfg()
            model = Keli10KModel(cfg)
            model.load(str(ckpt))
            model.model.eval()
            print(f'  Model loaded: {ckpt.name}')
        else:
            print('  No checkpoint found, running in fallback mode')
    except Exception as e:
        print(f'  Model load failed: {e}')
        model = None


# --- Tutor Lessons ---
TUTOR_LESSONS = {
    'html page': {
        'title': 'HTML Page',
        'steps': [
            {'instruction': 'Create an HTML file with <!DOCTYPE html>', 'check': '<!DOCTYPE html>', 'hint': 'Start with <!DOCTYPE html>'},
            {'instruction': 'Add <html>, <head>, and <body> tags', 'check': '<html>.*<head>.*<body>', 'hint': 'Structure: html > head + body'},
            {'instruction': 'Add a <title> tag in the head', 'check': '<title>', 'hint': '<title>Your Title</title>'},
            {'instruction': 'Add an <h1> heading in the body', 'check': '<h1>', 'hint': '<h1>Hello World</h1>'},
        ]
    },
    'javascript function': {
        'title': 'JavaScript Function',
        'steps': [
            {'instruction': 'Define a function with function keyword', 'check': 'function\\s+\\w+\\s*\\(', 'hint': 'function myFunc() {'},
            {'instruction': 'Add a parameter', 'check': 'function\\s+\\w+\\s*\\(\\w+', 'hint': 'function greet(name) {'},
            {'instruction': 'Return a value', 'check': 'return\\s+', 'hint': 'return "Hello " + name;'},
            {'instruction': 'Call the function', 'check': '\\w+\\s*\\(', 'hint': 'greet("World");'},
        ]
    },
    'css style': {
        'title': 'CSS Style',
        'steps': [
            {'instruction': 'Create a CSS rule with a selector', 'check': '\\w+\\s*\\{', 'hint': 'body {'},
            {'instruction': 'Set the color property', 'check': 'color\\s*:', 'hint': 'color: blue;'},
            {'instruction': 'Set the font-size property', 'check': 'font-size\\s*:', 'hint': 'font-size: 16px;'},
            {'instruction': 'Add a margin or padding', 'check': '(margin|padding)\\s*:', 'hint': 'margin: 10px;'},
        ]
    },
    'react component': {
        'title': 'React Component',
        'steps': [
            {'instruction': 'Import React', 'check': 'import\\s+React', 'hint': "import React from 'react';"},
            {'instruction': 'Create a functional component', 'check': 'function\\s+\\w+\\s*\\(', 'hint': 'function App() {'},
            {'instruction': 'Return JSX', 'check': 'return\\s*\\(', 'hint': 'return (<div>...</div>);'},
            {'instruction': 'Export the component', 'check': 'export\\s+default', 'hint': 'export default App;'},
        ]
    },
    'python class': {
        'title': 'Python Class',
        'steps': [
            {'instruction': 'Define a class', 'check': 'class\\s+\\w+', 'hint': 'class MyClass:'},
            {'instruction': 'Add an __init__ method', 'check': 'def\\s+__init__', 'hint': 'def __init__(self):'},
            {'instruction': 'Add a method with self parameter', 'check': 'def\\s+\\w+\\s*\\(self', 'hint': 'def method(self):'},
            {'instruction': 'Create an instance', 'check': '\\w+\\s*=\\s*\\w+\\s*\\(', 'hint': 'obj = MyClass()'},
        ]
    },
}


# --- Response Builders ---

def build_chat_response(query):
    query_lower = query.lower()

    # Tutor mode
    for key in TUTOR_LESSONS:
        if key in query_lower or ('teach me' in query_lower and key.split()[0] in query_lower):
            lesson = TUTOR_LESSONS[key]
            return {
                'response': f"Opening tutor mode for {lesson['title']}. Follow the steps in the tutor panel.",
                'mode': 'tutor',
                'tutor_lesson': key,
            }

    # Model-based response
    if model is not None and tok is not None and generate_fn is not None:
        try:
            prompt = f"<BOS>user: {query}\nassistant:"
            result = generate_fn(model, prompt, max_tokens=128)
            if result and result.get('text'):
                text = result['text']
                conf = result['confidence']
                response_text = text
                if conf['avg'] < 0.3:
                    response_text += "\n\n_(I'm not very confident about this answer)_"
                return {
                    'response': response_text,
                    'confidence': conf,
                    'citations': ['keli-knowledge-base'] if conf['avg'] > 0.5 else [],
                }
        except Exception as e:
            print(f'  Model inference failed: {e}')

    # Fallback responses
    responses = {
        'hello': 'Hey dumbass. What do you want to build?',
        'hi': 'Hey dumbass. What do you want to build?',
        'help': 'I can build code, explain things, teach you, debug, and ship projects.',
        'build': 'What should I build? Give me a description.',
        'design': 'I can help with CSS, layout, and visual design. What\'re we making?',
        'debug': 'Paste your code and I\'ll find the bugs.',
        'teach': 'What do you want to learn? I have lessons on HTML, CSS, JS, React, and Python.',
    }
    for key, resp in responses.items():
        if key in query_lower:
            return {'response': resp}

    return {'response': f'I\'m still learning. Try asking me to build something specific.'}


def build_build_response(task, existing_files):
    task_lower = task.lower()

    if 'html' in task_lower or 'page' in task_lower or 'website' in task_lower:
        return build_html_page(task)
    elif 'react' in task_lower or 'component' in task_lower:
        return build_react_component(task)
    elif 'python' in task_lower or 'script' in task_lower:
        return build_python_script(task)
    elif 'css' in task_lower or 'style' in task_lower:
        return build_css_file(task)
    elif 'function' in task_lower or 'helper' in task_lower:
        return build_js_function(task)
    elif 'api' in task_lower or 'server' in task_lower:
        return build_api_server(task)
    elif 'debug' in task_lower or 'fix' in task_lower:
        return build_debug(task, existing_files)
    elif 'fullstack' in task_lower or 'app' in task_lower:
        return build_fullstack_app(task)
    else:
        # Default: build JS
        return build_js_function(task)


def build_html_page(task):
    name = re.findall(r'\w+', task)[0] if re.findall(r'\w+', task) else 'page'
    title = name.capitalize()
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div id="app">
<h1>{title}</h1>
<p>Your content here.</p>
</div>
<script src="app.js"></script>
</body>
</html>'''
    css = '''* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: linear-gradient(135deg, #0a1628, #1a1a2e); color: #c0d6e4;
       min-height: 100vh; display: flex; justify-content: center; align-items: center; }
#app { text-align: center; padding: 2rem; }
h1 { font-size: 2.5rem; margin-bottom: 1rem;
     background: linear-gradient(90deg, #00e5ff, #b967ff); -webkit-background-clip: text;
     -webkit-text-fill-color: transparent; }
p { font-size: 1.2rem; opacity: 0.8; }'''
    js = '''console.log('App loaded');
document.addEventListener('DOMContentLoaded', () => {
  document.querySelector('h1').addEventListener('click', () => {
    alert('Hello from Keli!');
  });
});'''
    return {'files': {'index.html': html, 'style.css': css, 'app.js': js}, 'territories': ['frontend']}


def build_react_component(task):
    name = re.findall(r'\w+', task)[0].capitalize() if re.findall(r'\w+', task) else 'App'
    jsx = f'''import React, {{ useState }} from 'react';

function {name}(props) {{
  const [count, setCount] = useState(0);

  return (
    <div className="{name.lower()}-container">
      <h1>{name} Component</h1>
      <p>Count: {{count}}</p>
      <button onClick={{() => setCount(c => c + 1)}}>Increment</button>
    </div>
  );
}}

export default {name};
'''
    css = f'''.{name.lower()}-container {{
  padding: 2rem;
  text-align: center;
}}
.{name.lower()}-container h1 {{
  color: #00e5ff;
  margin-bottom: 1rem;
}}
.{name.lower()}-container button {{
  background: linear-gradient(90deg, #00e5ff, #b967ff);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}}'''
    return {'files': {f'{name}.jsx': jsx, f'{name}.css': css}, 'territories': ['frontend', 'react']}


def build_python_script(task):
    name = re.findall(r'\w+', task)[0] if re.findall(r'\w+', task) else 'script'
    py = f'''import sys
import json


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    print(f"Running {name} with args: {{args}}")
    result = {{
        "status": "ok",
        "message": f"Hello from {{name}}",
        "args": args,
    }}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
'''
    return {'files': {f'{name}.py': py}, 'territories': ['backend']}


def build_css_file(task):
    css = '''/* Arctic Fusion Theme */
:root {
  --bg-deep: #0a1628;
  --bg-surface: #121e30;
  --primary: #00e5ff;
  --secondary: #b967ff;
  --text: #c0d6e4;
  --text-muted: #6b8299;
  --border: rgba(0, 229, 255, 0.15);
  --glass: rgba(10, 22, 40, 0.6);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-deep);
  color: var(--text);
  min-height: 100vh;
}

.glass {
  background: var(--glass);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.gradient-text {
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.btn {
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:hover { opacity: 0.85; }
'''
    return {'files': {'theme.css': css}, 'territories': ['design']}


def build_js_function(task):
    name = re.findall(r'\w+', task)[0] if re.findall(r'\w+', task) else 'helperFunction'
    js = f'''/**
 * {name} - Generated by Keli
 */

function {name}(input) {{
  // TODO: implement
  if (input === undefined || input === null) {{
    return null;
  }}
  return input;
}}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {{
  module.exports = {{ {name} }};
}}
'''
    return {'files': {f'{name}.js': js}, 'territories': ['backend']}


def build_api_server(task):
    fastapi = '''from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Keli API")

class Item(BaseModel):
    name: str
    value: float = 0.0

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/items")
def create_item(item: Item):
    return {"id": hash(item.name) % 10000, "name": item.name, "value": item.value}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    return {'files': {'main.py': fastapi}, 'territories': ['backend']}


def build_debug(task, existing_files):
    fixes = {}
    logs = []

    for fname, content in (existing_files or {}).items():
        fixed = content
        changes = []

        if 'console.log' in content and ';' not in content:
            pass  # Fine for JS
        if 'var ' in content:
            fixed = fixed.replace('var ', 'const ')
            changes.append('var -> const')
        if '==' in content and '===' not in content:
            fixed = re.sub(r'(?<![!=])==(?!=)', '===', fixed)
            changes.append('== -> ===')
        if content.strip().endswith(';') and content.strip().endswith(';\n'):
            # Already has semicolons
            pass

        if changes:
            fixes[fname] = fixed
            logs.append(f'{fname}: fixed {", ".join(changes)}')

    return {
        'files': fixes,
        'debug_log': logs,
        'territories': ['debug'],
    }


def build_fullstack_app(task):
    name = re.findall(r'\w+', task)[0].capitalize() if re.findall(r'\w+', task) else 'App'
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div id="root"></div>
<script src="app.js"></script>
</body>
</html>'''
    js = f'''import React, {{ useState, useEffect }} from 'react';
import ReactDOM from 'react-dom';

function {name}() {{
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    fetch('/api/data')
      .then(r => r.json())
      .then(d => {{ setData(d); setLoading(false); }})
      .catch(() => setLoading(false));
  }}, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="app">
      <h1>{name}</h1>
      <pre>{{JSON.stringify(data, null, 2)}}</pre>
    </div>
  );
}}

ReactDOM.render(<{name} />, document.getElementById('root'));
'''
    css = '''.app { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.app h1 { color: #00e5ff; margin-bottom: 1rem; }
pre { background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; overflow-x: auto; }'''
    py = f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/data")
def get_data():
    return {{"app": "{name}", "version": "1.0", "status": "running"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    return {
        'files': {'index.html': html, 'app.js': js, 'style.css': css, 'backend.py': py},
        'territories': ['frontend', 'backend', 'fullstack'],
    }


def build_preview_response(files):
    html_content = None
    console_outputs = []
    errors = []

    for fname, content in (files or {}).items():
        if fname.endswith('.html'):
            html_content = content
        elif fname.endswith('.js'):
            # Simple JS lint check
            if 'import ' in content and 'React' in content:
                console_outputs.append('[info] React/JSX detected - needs build step')
            if 'debugger' in content:
                console_outputs.append('[warn] debugger statement found')
        elif fname.endswith('.css'):
            # Check for common CSS issues
            if '{' not in content:
                errors.append(f'{fname}: No CSS rules found')
            if '}' in content and content.count('{') != content.count('}'):
                errors.append(f'{fname}: Mismatched braces')

    if not html_content:
        # Generate a wrapper page that includes all JS/CSS
        js_tags = ''
        css_tags = ''
        for fname, content in (files or {}).items():
            if fname.endswith('.js'):
                js_tags += f'<script>\\n{content}\\n<\\/script>\\n'
            elif fname.endswith('.css'):
                css_tags += f'<style>\\n{content}\\n</style>\\n'

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Preview</title>
{css_tags}
</head>
<body>
<div id="root"></div>
{js_tags}
</body>
</html>'''

    return {
        'rendered_html': html_content,
        'console_output': console_outputs,
        'errors': errors,
    }


def build_export_response(files, fmt):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname, content in (files or {}).items():
            zf.writestr(fname, content)
    buf.seek(0)
    return buf


def build_code_check_response(code, lang):
    checks = []
    if lang == 'python':
        if 'import' in code and code.count('import') > code.count('\n') / 3:
            checks.append({'severity': 'warn', 'message': 'Many imports - consider grouping'})
        if 'try' in code and 'except' not in code:
            checks.append({'severity': 'error', 'message': 'try without except'})
        if ':' in code and 'def' not in code and 'class' not in code and 'if' not in code and 'for' not in code and 'while' not in code:
            checks.append({'severity': 'info', 'message': 'Colon found outside control flow'})
    elif lang in ('js', 'javascript'):
        if 'var ' in code:
            checks.append({'severity': 'warn', 'message': 'Use const/let instead of var'})
        if '==' in code and '===' not in code:
            checks.append({'severity': 'warn', 'message': 'Use === instead of =='})
        if 'console.log' in code and code.count('console.log') > 3:
            checks.append({'severity': 'info', 'message': f'{code.count("console.log")} console.log statements'})
    elif lang == 'html':
        if '<!DOCTYPE html>' not in code.upper():
            checks.append({'severity': 'warn', 'message': 'Missing DOCTYPE declaration'})
        if '<meta charset' not in code.lower():
            checks.append({'severity': 'warn', 'message': 'Missing charset meta tag'})
    elif lang == 'css':
        if '{' not in code:
            checks.append({'severity': 'error', 'message': 'No CSS rules found'})
    return {'checks': checks}


# --- HTTP Server ---

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f'  [{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}')

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == '/health':
            return self._send_json({'status': 'ok'})

        if path.startswith('/download/'):
            zip_rel = path[len('/download/'):]
            zip_path = Path('/tmp/opencode/snca/exports') / zip_rel
            if zip_path.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Disposition', f'attachment; filename="{zip_path.name}"')
                self.send_header('Content-Length', str(zip_path.stat().st_size))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(zip_path, 'rb') as f:
                    shutil.copyfileobj(f, self.wfile)
                return
            return self._send_json({'error': 'File not found'}, 404)

        self._send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()

        if path == '/chat':
            query = body.get('query', '')
            session_id = body.get('session_id')
            result = build_chat_response(query)
            return self._send_json(result)

        elif path == '/build':
            task = body.get('task', '')
            existing_files = body.get('existing_files', {})
            session_id = body.get('session_id')
            result = build_build_response(task, existing_files)
            return self._send_json(result)

        elif path == '/preview':
            files = body.get('files', {})
            result = build_preview_response(files)
            return self._send_json(result)

        elif path == '/export':
            files = body.get('files', {})
            fmt = body.get('format', 'static')
            zip_buf = build_export_response(files, fmt)

            export_dir = Path('/tmp/opencode/snca/exports')
            export_dir.mkdir(parents=True, exist_ok=True)
            zip_name = f'keli_export_{int(time.time())}.zip'
            zip_path = export_dir / zip_name
            with open(zip_path, 'wb') as f:
                f.write(zip_buf.getvalue())

            return self._send_json({
                'zip_path': str(zip_path),
                'download_url': f'/download/{zip_name}',
            })

        elif path == '/swarm_status':
            if model is not None and hasattr(model, 'get_utilization'):
                try:
                    util = model.get_utilization()
                    return self._send_json({
                        'total_bots': util.get('total_bots', 10000),
                        'awake_bots': util.get('active_bots', 0),
                        'awake_pct': util.get('bot_utilization_pct', 0),
                        'territory_balance': util.get('territory_load', {}),
                        'comm_load': util.get('communication_density', 0),
                        'coordinator_consensus': 0.94,
                    })
                except Exception as e:
                    return self._send_json({'error': str(e)}, 500)
            return self._send_json({
                'total_bots': 10000, 'awake_bots': 0, 'awake_pct': 0,
                'message': 'Model not loaded',
            })

        elif path == '/run':
            code = body.get('code', '')
            lang = body.get('type', 'js')
            result = build_code_check_response(code, lang)
            return self._send_json(result)

        elif path == '/check':
            code = body.get('code', '')
            lang = body.get('lang', 'javascript')
            result = build_code_check_response(code, lang)
            return self._send_json(result)

        elif path == '/tutor/lesson':
            lesson_key = body.get('lesson', '')
            lesson = TUTOR_LESSONS.get(lesson_key)
            if lesson:
                return self._send_json(lesson)
            return self._send_json({'error': 'Lesson not found'}, 404)

        elif path == '/tutor/check':
            code = body.get('code', '')
            step = body.get('step', {})
            pattern = step.get('check', '')
            if re.search(pattern, code, re.DOTALL):
                return self._send_json({'passed': True, 'message': 'Step completed!'})
            return self._send_json({'passed': False, 'message': step.get('hint', 'Try again')})

        else:
            self._send_json({'error': 'Not found'}, 404)


def main():
    import time

    print(f'Keli API Server starting on {HOST}:{PORT}')
    try_load_model()
    print(f'Server ready on http://{HOST}:{PORT}')

    server = HTTPServer((HOST, PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.shutdown()


if __name__ == '__main__':
    main()
