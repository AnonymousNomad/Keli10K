import subprocess
import tempfile
import os
import re
import json
import zipfile
import io
import traceback
from pathlib import Path

CAPTURE_TIMEOUT_MS = 5000
MAX_OUTPUT_LEN = 10000

class BuildResult:
    def __init__(self, success=False, output='', error='', files=None):
        self.success = success
        self.output = output[:MAX_OUTPUT_LEN]
        self.error = error[:MAX_OUTPUT_LEN]
        self.files = files or {}

    def to_dict(self):
        return {'success': self.success, 'output': self.output, 'error': self.error, 'files': self.files}


class SandboxError(Exception):
    pass


def _strip_console_artifacts(text):
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()


class HTMLSandbox:
    def __init__(self, timeout_ms=CAPTURE_TIMEOUT_MS):
        self.timeout_ms = timeout_ms

    def execute(self, code):
        errors = re.findall(r'(?:Error|throw|reject|SyntaxError|TypeError|ReferenceError)\s*[:\(]', code)
        if errors:
            first = errors[0].rstrip(':(')
            return BuildResult(success=False, error=f'Static analysis flagged: {first} in source')

        html = '<!DOCTYPE html><html><head><meta charset="UTF-8">'
        html += '<style>body{font-family:sans-serif;padding:16px;background:#fff;color:#333}</style>'
        html += '</head><body>'
        html += '<div id="app"></div>'
        html += '<script>'
        html += 'window.onerror = function(m,s,l,c,e) { document.body.innerHTML += "<pre style=color:red>ERROR: " + m + " (" + s + ":" + l + ")</pre>"; };'
        html += code
        html += '\nconsole.log("Execution completed");'
        html += '</script></body></html>'

        return BuildResult(success=True, output='HTML preview generated', files={'index.html': html})


class PythonSandbox:
    def __init__(self, timeout_ms=CAPTURE_TIMEOUT_MS):
        self.timeout_ms = timeout_ms

    def execute(self, code):
        banned = ['__import__', 'eval(', 'exec(', 'compile(', 'open(', 'os.system', 'subprocess']
        for b in banned:
            if b in code:
                return BuildResult(success=False, error=f'Blocked function: {b}')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            tmp_path = f.name

        try:
            result = subprocess.run(
                ['python3', '-c', code],
                capture_output=True, text=True,
                timeout=self.timeout_ms / 1000,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
            )
            stdout = _strip_console_artifacts(result.stdout)
            stderr = _strip_console_artifacts(result.stderr)

            if result.returncode == 0:
                return BuildResult(success=True, output=stdout or 'Execution completed')
            else:
                return BuildResult(success=False, error=stderr or f'Exit code {result.returncode}')
        except subprocess.TimeoutExpired:
            return BuildResult(success=False, error=f'Execution timed out after {self.timeout_ms}ms')
        except Exception as e:
            return BuildResult(success=False, error=str(e))
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass


class BuildEngine:
    LANGUAGES = {
        'html': HTMLSandbox,
        'js': HTMLSandbox,
        'jsx': HTMLSandbox,
        'py': PythonSandbox,
        'python': PythonSandbox,
    }

    def __init__(self, governor=None):
        self.governor = governor
        self._sandboxes = {}

    def _get_or_create(self, lang):
        cls = self.LANGUAGES.get(lang)
        if cls is None:
            return None
        if lang not in self._sandboxes:
            self._sandboxes[lang] = cls()
        return self._sandboxes[lang]

    def execute(self, code, lang='py', max_retries=3):
        lang = lang.lower().lstrip('.')
        sandbox = self._get_or_create(lang)
        if sandbox is None:
            return BuildResult(success=False, error=f'No sandbox for language: {lang}')

        last_error = ''
        for attempt in range(max_retries):
            try:
                result = sandbox.execute(code)
                if result.success:
                    if self.governor and hasattr(self.governor, 'heal_output'):
                        result = self.governor.heal_output(result)
                    return result
                last_error = result.error
                if attempt < max_retries - 1:
                    code = self._self_heal(code, result.error)
            except SandboxError as e:
                last_error = str(e)
                break
            except Exception as e:
                last_error = f'Execution crash: {e}'
                break

        return BuildResult(success=False, error=f'Failed after {max_retries} retries. Last: {last_error}')

    def _self_heal(self, code, error):
        error_lower = error.lower()
        patches = [
            (r'\b(var|let|const)\s+(\w+)\s*=(?!.*;)', r'\1 \2 = null; // auto-fixed'),
        ]
        for pattern, replacement in patches:
            code = re.sub(pattern, replacement, code)
        if 'import' in error_lower and 'not found' in error_lower:
            code = re.sub(r'^(import\s+\S+)', r'# \1  # disabled by self-heal', code, flags=re.MULTILINE)
        if 'indentationerror' in error_lower or 'unexpected indent' in error_lower:
            lines = code.split('\n')
            fixed = []
            for l in lines:
                stripped = l.lstrip()
                if stripped and not stripped.startswith('#') and len(l) - len(stripped) > 0:
                    l = '    ' + stripped if len(l) - len(stripped) < 4 else l
                fixed.append(l)
            code = '\n'.join(fixed)
        return code

    def preview_html(self, code, lang='html'):
        lang = lang.lower().lstrip('.')
        if lang in ('html', 'js', 'jsx'):
            sandbox = self._get_or_create('html')
            result = sandbox.execute(code)
            if result.success and 'index.html' in result.files:
                return result.files['index.html']
        return None


def create_static_zip(files_dict, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, content in files_dict.items():
            zf.writestr(name, content)
    return str(Path(output_path).resolve())


def create_pwa_zip(files_dict, output_path):
    manifest = {
        "name": "SNCA Keli App",
        "short_name": "Keli",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a2a2a",
        "theme_color": "#1a6b6b",
        "icons": [{"src": "/icon.png", "sizes": "192x192", "type": "image/png"}],
    }
    service_worker = """
self.addEventListener('install', (e) => e.waitUntil(self.skipWaiting()));
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', (e) => e.respondWith(
  caches.match(e.request).then((r) => r || fetch(e.request))
));
"""
    files_dict['manifest.json'] = json.dumps(manifest, indent=2)
    files_dict['service-worker.js'] = service_worker.strip()

    return create_static_zip(files_dict, output_path)


def assemble_preview_html(files_dict):
    css = files_dict.get('style.css', '')
    js = files_dict.get('app.js', '')
    raw_html = files_dict.get('index.html', '')

    js = re.sub(r'<script\s+[^>]*src\s*=\s*["\']https?://[^"\']+["\'][^>]*>.*?</script>', '', js, flags=re.DOTALL)

    console_proxy = """
window._console = [];
var _origLog = console.log;
console.log = function() {
  var args = Array.prototype.slice.call(arguments).join(' ');
  window._console.push(args);
  _origLog.apply(console, arguments);
};
console.error = function() {
  var args = Array.prototype.slice.call(arguments).join(' ');
  window._console.push('[ERROR] ' + args);
};
"""
    post_msg = 'document.addEventListener("DOMContentLoaded",function(){window._console&&window.parent&&window.parent.postMessage({type:"snca-console",data:window._console},"*");});'

    if '<html' in raw_html or '<head' in raw_html or '<body' in raw_html:
        html = raw_html
        html = html.replace('</head>', f'<style>{css}</style></head>') if css in html else html
        html = html.replace('</head>', f'<script>{console_proxy}</script></head>')
        html = html.replace('</body>', f'<script>{js}</script></body>') if js in html else html
        html = html.replace('</body>', f'<script>{post_msg}</script></body>')
    else:
        html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><style>' + css + '</style><script>' + console_proxy + '</script></head><body>'
        html += raw_html if raw_html else '<div id="root"></div>'
        html += '<script>' + js + '</script>'
        html += '<script>' + post_msg + '</script>'
        html += '</body></html>'

    return html


if __name__ == '__main__':
    be = BuildEngine()
    tests = [
        ('print("Hello from Python sandbox")', 'py'),
        ('<h1>Hello HTML</h1><script>alert("js ok")</script>', 'html'),
        ('function test() { return 1; } console.log(test())', 'js'),
    ]
    for code, lang in tests:
        result = be.execute(code, lang)
        print(f"[{lang}] success={result.success}")
        if result.output: print(f"  output: {result.output[:80]}")
        if result.error: print(f"  error: {result.error[:80]}")

    print("\n--- Zip Test ---")
    files = {'index.html': '<h1>Hello</h1>', 'app.js': 'console.log("hi")'}
    zip_path = create_static_zip(files, '/tmp/test_build.zip')
    print(f"Static zip: {zip_path}")
    zip_path2 = create_pwa_zip(files, '/tmp/test_pwa.zip')
    print(f"PWA zip: {zip_path2}")

    print("\n--- Preview Assembly Test ---")
    html = assemble_preview_html(files)
    print(f"Preview HTML length: {len(html)} chars")
