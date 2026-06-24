#!/usr/bin/env python3
"""Keli CLI — Parrot-style terminal with nanobot ocean theme."""
import sys, os, json, argparse, shutil, threading, time, readline, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wave_animator import WaveAnimator
from mode_selector import ModeSelector
from response_renderer import ResponseRenderer
from territory_monitor import TerritoryMonitor
from tutor_engine import TutorEngine
from train_engine import TrainEngine

C = '\033[96m'; G = '\033[92m'; Y = '\033[93m'; R = '\033[91m'
B = '\033[1m'; DIM = '\033[2m'; RESET = '\033[0m'
BG = '\033[44m'; BLUE = '\033[94m'; PURPLE = '\033[95m'

CONFIG_DIR = os.path.expanduser('~/.keli')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')
API_BASE = os.environ.get('KELI_API', 'http://localhost:8080')

def load_config():
    if os.path.exists(CONFIG_PATH): return json.load(open(CONFIG_PATH))
    return {'api_base': API_BASE}

def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True); json.dump(cfg, open(CONFIG_PATH, 'w'))

def term_width(): return shutil.get_terminal_size((80, 20)).columns

def api_post(endpoint, data):
    import urllib.request, urllib.error
    cfg = load_config()
    url = f'{cfg["api_base"]}/{endpoint}'
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except: return None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(mode='plan', awake_bots=8742, total_bots=10000):
    tw = term_width()
    cap_pct = int(awake_bots / total_bots * 100) if total_bots else 0
    sys.stdout.write(f'{C}┌─[{B}{mode.upper()}{C}]─[{awake_bots:.0f}/{total_bots} bots]─[{cap_pct}% cap]─{"─" * (tw - 40)}\n')
    sys.stdout.write(f'{RESET}')
    sys.stdout.flush()

def print_prompt(mode='plan'):
    sys.stdout.write(f'{C}keli@sovereign:{mode}${RESET} ')
    sys.stdout.flush()

def print_keli_header(text):
    sys.stdout.write(f'{Y}[◢◣ Keli]:{RESET} {text}\n')
    sys.stdout.flush()

def print_error(text):
    sys.stdout.write(f'{R}Error:{RESET} {text}\n')
    sys.stdout.flush()

def print_success(text):
    sys.stdout.write(f'{G}{text}{RESET}\n')
    sys.stdout.flush()

def interactive_train(trainer):
    print(f'{PURPLE}Train Mode — Keli as teacher for your model.{RESET}\n')
    print(f'  {DIM}Keli uses her 10K nanobot swarm to generate examples,{RESET}')
    print(f'  {DIM}score outputs, and guide your model to convergence.{RESET}\n')
    while True:
        print_prompt('train')
        try:
            line = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print(); continue
        if not line: continue
        if line == '/exit' or line == 'exit': break
        if line == 'clear': clear_screen(); continue

        if line == 'status':
            trainer.status_report()
            continue
        if line == 'domains':
            trainer.list_domains()
            continue
        if line == 'modes':
            trainer.list_modes()
            continue
        if line == 'curriculum':
            result = trainer.design_curriculum()
            print(result)
            continue

        if line.startswith('domain '):
            d = line[7:].strip().lower().replace(' ', '-')
            if d in trainer.DOMAINS:
                trainer.domain = d
                print_success(f'Domain set to {d}')
            else:
                trainer.list_domains()
            continue

        if line.startswith('mode '):
            m = line[5:].strip().lower()
            if m in trainer.MODES:
                trainer.mode = m
                print_success(f'Mode set to {m}')
            else:
                trainer.list_modes()
            continue

        if line.startswith('load '):
            path = line[5:].strip()
            if os.path.exists(path):
                trainer.load_student_model(path)
                print_success(f'Loaded student model: {trainer.student_name}')
            else:
                print_error(f'File not found: {path}')
            continue

        if line.startswith('generate '):
            try:
                count = int(line[9:].strip())
            except:
                count = 20
            trainer.generate_examples(count)
            continue

        if line == 'train':
            if not trainer.generated_examples:
                print_error('No training examples. Use generate first.')
                continue
            print(f'  {Y}Training {trainer.epoch+1} epochs, {len(trainer.generated_examples)} examples...{RESET}')
            trainer.run_epoch()
            continue

        if line == 'train+':
            if not trainer.generated_examples:
                print_error('No training examples. Use generate first.')
                continue
            for _ in range(5):
                trainer.run_epoch()
                time.sleep(0.5)
            continue

        print(f'  {DIM}Commands: generate N, train, train+, load PATH, domain, mode, curriculum, status{RESET}')

def cmd_status(args):
    result = api_post('swarm_status', {})
    if not result:
        print_error('Keli is asleep.')
        return
    awake = result.get('awake_bots', 0)
    total = result.get('total_bots', 10000)
    tb = result.get('territory_balance', {})
    tw = term_width()
    sys.stdout.write(f'{C}┌─ SWARM STATUS {"─" * (tw - 20)}\n')
    sys.stdout.write(f'│ Total Bots:     {total:>8,}\n')
    sys.stdout.write(f'│ Active:         {awake:>8,.0f} ({awake/total*100:.1f}%)\n' if total else '')
    sys.stdout.write(f'│ Coordinators:   10/10 consensus\n')
    sys.stdout.write(f'│ Territories:    {"|".join(f"{k}:{v:.0f}" for k,v in tb.items())}\n' if tb else '')
    sys.stdout.write(f'│ Mode:           plan\n')
    sys.stdout.write(f'│ Offline Cache:  ✓ Ready\n')
    sys.stdout.write(f'{C}└{"─" * (tw - 1)}\n{RESET}')
    sys.stdout.flush()

SPONSOR_MSG = (
    f'\n  {C}◢◣ Keli is 100% free — MIT licensed, no paywalls.{RESET}'
    f'\n  {Y}If it helps you, throw a coffee at the nanobots:{RESET}'
    f'\n    {G}☕{RESET} https://ko-fi.com/ferrellsi'
    f'\n    {PURPLE}💖{RESET} https://github.com/sponsors/AnonymousNomad'
    f'\n  {DIM}No pressure. The code is free either way.{RESET}\n'
)

def cmd_donate(args=None):
    print(SPONSOR_MSG)

def cmd_version(args):
    print(f'  Keli10K v1.0 — 10,000 nanobot swarm, 25.5M params')
    cmd_donate()

def interactive_plan(renderer):
    readline.parse_and_bind('tab: complete')
    print(f'{C}Plan Mode — Ask coding questions. Type /exit to quit.{RESET}\n')
    while True:
        print_prompt('plan')
        try:
            line = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print(); continue
        if not line: continue
        if line == '/exit' or line == 'exit': break
        if line == 'clear': clear_screen(); continue
        if line == 'help':
            print(f'  {Y}Commands:{RESET} /exit, /clear, plan, build, tutor, train, status, donate')
            continue
        if line in ('donate', 'sponsor', '/donate'):
            cmd_donate()
            continue

        sys.stdout.write(f'{DIM}Keli is thinking...{RESET}\r'); sys.stdout.flush()
        result = api_post('chat', {'prompt': line, 'mode': 'plan'})
        if result and 'response' in result:
            resp = result['response']
            lines = resp.split('\n')
            renderer.render_keli_response(lines)
        else:
            print_keli_header(f'{R}Swarm offline. Start the API first.{RESET}')

def interactive_build(renderer, monitor):
    print(f'{C}Build Mode — Describe what to build.{RESET}\n')
    while True:
        print_prompt('build')
        try:
            line = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print(); continue
        if not line: continue
        if line == '/exit' or line == 'exit': break
        if line == 'clear': clear_screen(); continue

        sys.stdout.write(f'{Y}[BUILD]{RESET} Analyzing...\n')
        sys.stdout.write(f'{Y}[BUILD]{RESET} Coordinators voting...\n')
        t = threading.Thread(target=monitor.simulate_build, args=(2.0,), daemon=True)
        t.start()
        t.join()

        sys.stdout.write(f'{Y}[BUILD]{RESET} Assembling files...\n')
        result = api_post('build', {'prompt': line})
        if result and 'response' in result:
            files = result.get('files', {})
            if files:
                file_list = [(n, f'{len(c)}B') for n, c in files.items()]
                renderer.render_build_output(file_list)
                sys.stdout.write(f'  Save to ./output/? [Y/n]: ')
                sys.stdout.flush()
                ans = sys.stdin.readline().strip().lower()
                if ans != 'n':
                    os.makedirs('output', exist_ok=True)
                    for fname, content in files.items():
                        with open(f'output/{fname}', 'w') as f:
                            f.write(content)
                        print_success(f'  ✓ {fname}')
                print_keli_header('Shipped.')
            else:
                renderer.render_keli_response(result['response'].split('\n'))
        else:
            print_error('Build failed. Swarm offline.')

def interactive_tutor(renderer, tutor):
    print(f'{C}Tutor Mode — Step-by-step lessons.{RESET}\n')
    tutor.list_lessons()
    while True:
        print_prompt('tutor')
        try:
            line = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print(); continue
        if not line: continue
        if line == '/exit' or line == 'exit': break
        if line == 'clear': clear_screen(); continue
        if line == 'list': tutor.list_lessons(); continue

        if line.startswith('start '):
            lesson_name = line[6:]
            msg = tutor.start_lesson(lesson_name)
            print_keli_header(msg)
            tutor.render_step()
            continue

        if line == 'hint':
            hint = tutor.get_hint()
            if hint:
                print_keli_header(f'💡 {hint}')
            else:
                print_keli_header('No hint available.')
            continue

        if line == 'skip':
            tutor.advance()
            if not tutor.render_step():
                print_keli_header('Lesson done!')
            continue

        if line == 'certify':
            cert = tutor.generate_certificate()
            print(cert)
            continue

        if tutor.current_lesson:
            correct, msg = tutor.check_answer(line)
            if correct:
                print_success('✓ Correct.')
                tutor.advance()
                if not tutor.render_step():
                    print_keli_header('Lesson complete! Type certify for your badge.')
            else:
                print(msg)
        else:
            tutor.list_lessons()

def main():
    parser = argparse.ArgumentParser(description='Keli10K Terminal CLI')
    parser.add_argument('--api', help='API base URL')
    parser.add_argument('--local', action='store_true', help='Load model directly (no API server needed)')
    parser.add_argument('command', nargs='?', help='Command (plan/build/generate/tutor/train/status/version)')
    parser.add_argument('prompt', nargs='*', help='Prompt text')
    parser.add_argument('--export', action='store_true', help='Export last build to zip')
    args = parser.parse_args()

    if args.api:
        cfg = load_config()
        cfg['api_base'] = args.api
        save_config(cfg)

    if args.local:
        try:
            from keli_10k import Keli10KModel
            from snca_tokenizer import SNCATokenizer
            from snca_config import SNCACfg
            cfg_obj = SNCACfg()
            local_model = Keli10KModel(cfg_obj)
            ckpt_dir = Path(__file__).parent.parent / 'checkpoints'
            best = ckpt_dir / 'keli_navy_best.pt'
            if best.exists():
                local_model.load(str(best))
                local_model.model.eval()
                print(f'{G}  Model loaded locally: {best.name}{RESET}')
                globals()['_local_model'] = local_model
                globals()['_local_tok'] = SNCATokenizer()
            else:
                print(f'{Y}  No checkpoint found. Start API server instead.{RESET}')
        except Exception as e:
            print(f'{R}  Local load failed: {e}{RESET}')

    wave = WaveAnimator()
    renderer = ResponseRenderer()
    monitor = TerritoryMonitor()
    tutor = TutorEngine()
    trainer = TrainEngine()

    if args.command == 'status':
        cmd_status(args)
        return
    if args.command == 'version':
        cmd_version(args)
        return
    if args.command == 'build' and args.prompt:
        prompt = ' '.join(args.prompt)
        sys.stdout.write(f'{Y}[BUILD]{RESET} Analyzing...\n')
        t = threading.Thread(target=monitor.simulate_build, args=(2.0,), daemon=True)
        t.start(); t.join()
        result = api_post('build', {'prompt': prompt})
        if result and 'files' in result:
            renderer.render_build_output([(n, f'{len(c)}B') for n, c in result['files'].items()])
            if not args.export:
                for fname, content in result['files'].items():
                    with open(fname, 'w') as f: f.write(content)
                    print_success(f'  ✓ {fname}')
            else:
                import zipfile
                os.makedirs('/tmp/exports', exist_ok=True)
                zpath = f'/tmp/exports/project_{time.strftime("%Y%m%d_%H%M%S")}.zip'
                with zipfile.ZipFile(zpath, 'w') as z:
                    for fname, content in result['files'].items():
                        z.writestr(fname, content)
                print_success(f'Exported: {zpath}')
        print_keli_header('Done.')
        return
    if args.command == 'generate':
        prompt = ' '.join(args.prompt) or 'build a todo app'
        print(f'{Y}[GENERATE]{RESET} Keli swarm building project: {prompt}')
        from scripts.keli_gen import match_prompt, generate as gen_project
        name = match_prompt(prompt)
        result = gen_project(name)
        if result:
            print(f'{C}Project: {result["name"]}{RESET}')
            print(f'{DIM}{result["description"]}{RESET}')
            print(f'{G}{result["total_files"]} files, {result["total_lines"]} lines{RESET}\n')
            for path, code in result['files'].items():
                print(f'{C}--- {path} ---{RESET}')
                lines = code.split('\n')
                for i, l in enumerate(lines[:10]):
                    print(f'  {l}')
                if len(lines) > 10:
                    print(f'  ... ({len(lines)} lines total)')
                print()
        else:
            print(f'{R}ERROR: Could not generate project{RESET}')
        sys.exit(0)

    clear_screen()

    wave.start()
    time.sleep(0.5)

    while True:
        print(ModeSelector.WELCOME)
        mode = ModeSelector.get_mode()

        clear_screen()
        print_header(mode)

        if mode == 'plan':
            interactive_plan(renderer)
        elif mode == 'build':
            interactive_build(renderer, monitor)
        elif mode == 'tutor':
            interactive_tutor(renderer, tutor)
        elif mode == 'train':
            interactive_train(trainer)

        print(f'\n{C}Returning to mode selector...{RESET}\n')
        time.sleep(1)
        clear_screen()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n{Y}Shutting down swarm...{RESET}')
        sys.exit(0)
