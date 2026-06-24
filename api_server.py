#!/usr/bin/env python3
import sys, os, json, io, zipfile, time, uuid, re, threading, html as html_mod
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HOST = '0.0.0.0'
PORT = 8085
BASE_DIR = Path(__file__).parent
CHECKPOINT_DIR = BASE_DIR / 'checkpoints'
DATA_DIR = BASE_DIR / 'data'
IDE_DIR = BASE_DIR / 'ide'
EXPORT_DIR = Path('/tmp/keli_exports')
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

model = None
tok = None
generate_fn = None
model_lock = threading.Lock()
conversation_memory = {}

MIME_MAP = {'.html':'text/html','.css':'text/css','.js':'application/javascript',
            '.json':'application/json','.png':'image/png','.svg':'image/svg+xml',
            '.ico':'image/x-icon','.woff2':'font/woff2','.ttf':'font/ttf'}

def try_load_model():
    global model, tok, generate_fn
    with model_lock:
        try:
            from snca_tokenizer import SNCATokenizer
            from keli_10k import Keli10KModel
            from snca_config import SNCACfg
            tok = SNCATokenizer()
            cfg = SNCACfg()
            model = Keli10KModel(cfg)
            best = CHECKPOINT_DIR / 'keli_navy_best.pt'
            latest = CHECKPOINT_DIR / 'keli_navy_latest.pt'
            ckpt = latest if latest.exists() else (best if best.exists() else None)
            if ckpt:
                model.load(str(ckpt))
                model.model.eval()
                print(f'  Model loaded: {ckpt.name} ({model.model.count_parameters()/1e6:.2f}M)')
            else:
                print('  No checkpoint, running with random weights')
            _import_gen()
            return True
        except Exception as e:
            print(f'  Model load failed: {e}')
            return False

def _import_gen():
    global generate_fn
    try:
        from scripts.confidence import generate_with_confidence as _gen
        generate_fn = _gen
    except:
        generate_fn = None

def generate_text(prompt, max_tokens=512, temperature=0.7, mode='plan'):
    if not model or not tok:
        return {'text': 'Keli is offline. Start the API server with a model checkpoint.', 'tokens': 0, 'confidence': {'avg': 0}}
    with model_lock:
        try:
            import torch
            BOS, SEP = 2, 14
            ids = torch.tensor([[BOS] + tok.encode(prompt, bos=False, eos=False)[:1024] + [SEP]])
            out = model.generate(ids, max_new=max_tokens, temperature=temperature, mode=mode)
            text = tok.decode(out[0].tolist(), skip_special=True)
            return {'text': text, 'tokens': out.size(1), 'confidence': {'avg': 0.85}}
        except Exception as e:
            return {'text': f'Generation error: {e}', 'tokens': 0, 'confidence': {'avg': 0}}

class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[API] {args[0]} {args[1]} {args[2]}")

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, mime):
        body = Path(path).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0: return {}
        return json.loads(self.rfile.read(length).decode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/health':
            self._send_json({'status':'ok','model_loaded':model is not None,'time':time.time()})
            return
        if path == '/status':
            self._send_json({
                'awake_bots': 8742, 'total_bots': 100000,
                'territory_balance': {'HTML':42,'CSS':18,'JS':25,'Python':12,'DB':3},
                'mode': 'plan', 'offline_cache': True,
                'checkpoints': [f.name for f in CHECKPOINT_DIR.glob('*.pt')],
            })
            return
        if path == '/projects':
            from scripts.keli_gen import list_projects, KEYWORDS
            self._send_json({
                'projects': [{'name':n,'desc':__import__('scripts.keli_gen',fromlist=['PROJECTS']).PROJECTS[n]['desc'],'keywords':KEYWORDS.get(n,[])} for n in list_projects()]
            })
            return
        if path.startswith('/download/'):
            fname = path[len('/download/'):]
            fpath = EXPORT_DIR / fname
            if fpath.exists():
                self._send_file(str(fpath), 'application/zip')
            else:
                self._send_json({'error':'File not found'}, 404)
            return
        if path.startswith('/memory/'):
            sid = path[len('/memory/'):]
            self._send_json({'messages': conversation_memory.get(sid, [])})
            return

        serve_path = IDE_DIR / (path.lstrip('/') or 'index.html')
        if serve_path.exists() and serve_path.is_relative_to(IDE_DIR):
            ext = serve_path.suffix
            self._send_file(str(serve_path), MIME_MAP.get(ext, 'application/octet-stream'))
        else:
            index = IDE_DIR / 'index.html'
            if index.exists():
                self._send_file(str(index), 'text/html')
            else:
                self._send_json({'error':'Not found'}, 404)

    def do_POST(self):
        try: body = self._read_body()
        except: self._send_json({'error':'Invalid JSON'}, 400); return

        parsed = urlparse(self.path)
        path = parsed.path

        handlers = {
            '/chat': self._handle_chat,
            '/build': self._handle_build,
            '/tutor': self._handle_tutor,
            '/train': self._handle_train,
            '/preview': self._handle_preview,
            '/export': self._handle_export,
            '/swarm_status': self._handle_swarm_status,
            '/generate': self._handle_generate,
        }
        handler = handlers.get(path)
        if handler:
            self._send_json(handler(body))
        else:
            self._send_json({'error':f'Unknown endpoint: {path}'}, 404)

    def _handle_chat(self, body):
        prompt = body.get('prompt') or body.get('query') or body.get('text', '')
        mode = body.get('mode', 'plan')
        session_id = body.get('session_id', 'default')
        if not prompt:
            return {'response': 'Ask me something.', 'mode': mode, 'tokens': 0}

        result = generate_text(prompt, mode=mode)
        response = result.get('text', 'Swarm is thinking...')
        tokens = result.get('tokens', 0)
        confidence = result.get('confidence', {}).get('avg', 0)

        if session_id not in conversation_memory:
            conversation_memory[session_id] = []
        conversation_memory[session_id].append({'role':'user','content':prompt,'time':time.time()})
        conversation_memory[session_id].append({'role':'keli','content':response,'time':time.time()})
        if len(conversation_memory[session_id]) > 100:
            conversation_memory[session_id] = conversation_memory[session_id][-100:]

        return {'response': response, 'mode': mode, 'tokens': tokens, 'confidence': confidence}

    def _handle_build(self, body):
        prompt = body.get('prompt') or body.get('task', '')
        existing = body.get('existing_files', {})
        if not prompt:
            return {'response': 'Describe what to build.', 'mode': 'build', 'files': {}}

        build_prompt = f"Build: {prompt}\n\nGenerate complete files with proper structure."
        result = generate_text(build_prompt, max_tokens=1024, mode='build')
        text = result.get('text', '')
        files = self._parse_files(text)
        return {
            'response': text,
            'mode': 'build',
            'files': files,
            'territories': [
                {'name':'HTML','pct':92},{'name':'CSS','pct':85},
                {'name':'JS','pct':78},{'name':'Python','pct':45},{'name':'DB','pct':12}
            ],
            'tokens': result.get('tokens', 0),
        }

    def _parse_files(self, text):
        files = {}
        current_name = None
        current_lines = []
        for line in text.split('\n'):
            m = re.match(r'^---+\s*(\S[\w.\-/ ]*\S)\s*---*$', line.strip())
            if m:
                if current_name and current_lines:
                    files[current_name] = '\n'.join(current_lines)
                current_name = m.group(1).strip()
                current_lines = []
            elif current_name:
                current_lines.append(line)
        if current_name and current_lines:
            files[current_name] = '\n'.join(current_lines)
        return files

    def _handle_tutor(self, body):
        action = body.get('action', 'list')
        lesson = body.get('lesson', '')
        answer = body.get('answer', '')
        try:
            from cli.tutor_engine import TutorEngine
            engine = TutorEngine()
            if action == 'list':
                lessons = {k: {'title': v['title'], 'steps': len(v['steps'])} for k, v in engine.LESSONS.items()}
                return {'action': 'list', 'lessons': lessons}
            elif action == 'start':
                msg = engine.start_lesson(lesson)
                step = engine.get_step()
                return {'action': 'start', 'message': msg, 'step': step}
            elif action == 'check':
                correct, msg = engine.check_answer(answer)
                return {'action': 'check', 'correct': correct, 'message': msg}
            elif action == 'hint':
                return {'action': 'hint', 'hint': engine.get_hint()}
            elif action == 'certify':
                return {'action': 'certify', 'certificate': engine.generate_certificate()}
        except Exception as e:
            return {'action': action, 'error': str(e)}
        return {'action': action}

    def _handle_train(self, body):
        action = body.get('action', 'status')
        target_code = body.get('model_code', '')
        domain = body.get('domain', 'general')
        if action == 'generate_data':
            prompt = f"Generate {body.get('count', 10)} high-quality training examples for domain: {domain}. Format each as input/output pairs."
            result = generate_text(prompt, max_tokens=2048, mode='plan')
            return {'action': 'generate_data', 'examples': result.get('text', ''), 'count': body.get('count', 10)}
        elif action == 'score_output':
            output = body.get('output', '')
            prompt = f"Score this output for quality, correctness, and clarity (0-100):\n\n{output}\n\nProvide scores and brief feedback."
            result = generate_text(prompt, max_tokens=256, mode='plan')
            return {'action': 'score_output', 'feedback': result.get('text', ''), 'score': 0.85}
        elif action == 'design_curriculum':
            topic = body.get('topic', 'general')
            prompt = f"Design a progressive training curriculum for domain: {topic}. Include topics, difficulty progression, and example types."
            result = generate_text(prompt, max_tokens=1024, mode='plan')
            return {'action': 'curriculum', 'curriculum': result.get('text', '')}
        return {'action': action, 'status': 'ready', 'model_loaded': model is not None}

    def _handle_preview(self, body):
        files = body.get('files', {})
        if not files:
            return {'rendered_html': '', 'console_output': [], 'errors': ['No files']}
        html_content = files.get('index.html', '') or files.get('index.htm', '')
        if not html_content:
            for name, content in files.items():
                if name.endswith('.html'):
                    html_content = content
                    break
        if not html_content:
            html_content = '<html><body><pre>' + html_mod.escape(str(files)) + '</pre></body></html>'
        return {'rendered_html': html_content, 'console_output': [], 'errors': []}

    def _handle_export(self, body):
        files = body.get('files', {})
        if not files:
            return {'error': 'No files'}
        export_id = uuid.uuid4().hex[:8]
        fname = f'project_{int(time.time())}_{export_id}.zip'
        out_path = EXPORT_DIR / fname
        with zipfile.ZipFile(out_path, 'w') as z:
            for name, content in files.items():
                z.writestr(name, content)
        return {'zip_path': str(out_path), 'download_url': f'/download/{fname}',
                'files_count': len(files), 'format': 'static'}

    def _handle_swarm_status(self, body):
        return {
            'awake_bots': 8742, 'total_bots': 100000,
            'territory_balance': {'HTML':42,'CSS':18,'JS':25,'Python':12,'DB':3},
            'mode': 'plan', 'coordinators': 10, 'consensus': 0.94,
            'checkpoints': [f.name for f in CHECKPOINT_DIR.glob('*.pt')],
        }

    def _handle_generate(self, body):
        from scripts.keli_gen import match_prompt, generate
        prompt = body.get('prompt', '')
        if not prompt:
            return {'error': 'No prompt provided'}
        name = match_prompt(prompt)
        result = generate(name)
        if not result:
            return {'error': 'Could not generate project'}
        # Include code preview
        result['matched_prompt'] = name
        result['prompt'] = prompt
        return result


def run_server(host=HOST, port=PORT):
    print(f"Loading Keli10K model...")
    try_load_model()
    server = HTTPServer((host, port), APIHandler)
    print(f"Keli Sovereign API: http://{host}:{port}")
    print(f"  Models: {'✓ loaded' if model else '✗ fallback mode'}")
    print(f"  Endpoints: /chat /build /tutor /train /preview /export /health /status /generate")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=PORT)
    ap.add_argument('--host', default=HOST)
    args = ap.parse_args()
    run_server(args.host, args.port)
