#!/usr/bin/env python3
"""Keli Sovereign IDE — unified launcher for API + IDE + CLI."""
import sys, os, threading, time, json

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

def start_api(host='0.0.0.0', port=8085, daemon=False):
    from api_server import run_server
    if daemon:
        t = threading.Thread(target=run_server, args=(host, port), daemon=True)
        t.start()
        print(f"  API server starting on http://{host}:{port} (background)")
        time.sleep(0.5)
        return t
    else:
        run_server(host, port)

def start_cli(local=False, api_url=None):
    from cli.keli import main
    sys.argv = [sys.argv[0]]
    if local:
        sys.argv.append('--local')
    if api_url:
        sys.argv.extend(['--api', api_url])
    main()

def health_check(host='127.0.0.1', port=8085):
    import urllib.request
    try:
        resp = urllib.request.urlopen(f'http://{host}:{port}/health', timeout=5)
        return json.loads(resp.read())
    except:
        return {'status': 'offline'}

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Keli Sovereign Launcher')
    ap.add_argument('--mode', choices=['api', 'cli', 'ide', 'all'], default='all',
                   help='Launch mode: api, cli, ide (api+web), or all')
    ap.add_argument('--port', type=int, default=8085)
    ap.add_argument('--host', default='0.0.0.0')
    ap.add_argument('--local', action='store_true', help='CLI: load model directly')
    args = ap.parse_args()

    print(f'\n  \033[96m◢◣ Keli Sovereign IDE v2.0\033[0m')
    print(f'  \033[94m10,000 nanobot swarm — 25.1M parameters\033[0m\n')

    if args.mode in ('api', 'all'):
        start_api(args.host, args.port, daemon=(args.mode == 'all'))

    if args.mode in ('cli', 'all') and args.mode != 'ide':
        api_url = f'http://{args.host}:{args.port}' if args.mode == 'all' else None
        start_cli(local=args.local or args.mode == 'cli', api_url=api_url)

    if args.mode == 'ide':
        print(f'  Starting API + IDE server on http://{args.host}:{args.port}')
        start_api(args.host, args.port)
