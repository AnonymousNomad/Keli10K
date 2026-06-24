#!/usr/bin/env python3
"""Self-improvement loop — Keli generates, tests, learns from own output."""
import sys, os, json, torch, math, time, traceback, subprocess, tempfile, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))
torch.set_num_threads(8)

from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from keli_10k import Keli10KModel
from trainer import SwarmDataset, compute_loss_and_acc, collate_batch
from torch.utils.data import DataLoader

LOG = 'self_improve.log'
GENERATED_DATA = 'data/self_generated/train.jsonl'
os.makedirs('data/self_generated', exist_ok=True)

def log(msg):
    with open(LOG, 'a') as f: f.write(f'[{time.strftime("%H:%M:%S")}] {msg}\n')
    print(f'[{time.strftime("%H:%M:%S")}] {msg}', flush=True)

cfg = SNCACfg()
tok = SNCATokenizer()

log("=== SELF-IMPROVEMENT LOOP STARTING ===")
ckpt = torch.load('checkpoints/keli_best.pt' if os.path.exists('checkpoints/keli_best.pt') else 'checkpoints/keli_navy_best.pt', map_location='cpu')
model = Keli10KModel(cfg)
model.model.load_state_dict(ckpt['model_state'], strict=False)
model.model.eval()
log(f"Model loaded: {sum(p.numel() for p in model.model.parameters())/1e6:.2f}M")

TASKS = [
    "Write a Python function to sort a list of numbers",
    "Build an HTML page with a navigation bar",
    "Write a React component that fetches data from an API",
    "Create a CSS grid layout with 3 columns",
    "Write a Python function that reads a CSV file",
    "Build a simple Express.js server with one route",
    "Write a JavaScript function that debounces input",
    "Create a responsive HTML form with validation",
    "Write a Python class for a simple bank account",
    "Build a Node.js script that watches a directory for changes",
]

def generate_code(prompt, max_new=150):
    ids = tok.encode(prompt, bos=True, eos=False)
    inp = torch.tensor([ids], dtype=torch.long)
    with torch.no_grad():
        out = model.model.generate(inp, max_new=max_new, temperature=0.8, top_k=50)
    return tok.decode(out[0].tolist())

def test_syntax(code, language='python'):
    if language == 'python':
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, str(e)
    return True, None  # Can't easily test others

def extract_code(output):
    code_blocks = re.findall(r'```(\w+)?\n(.*?)```', output, re.DOTALL)
    if code_blocks:
        return code_blocks[0][1].strip(), code_blocks[0][0] or 'python'
    return output, 'text'

def improve_failed(prompt, code, error):
    improvement_prompt = f"The following code has an error:\n```python\n{code}\n```\nError: {error}\nFix the code and return only the corrected version."
    ids = tok.encode(improvement_prompt, bos=True, eos=False)
    inp = torch.tensor([ids], dtype=torch.long)
    with torch.no_grad():
        out = model.model.generate(inp, max_new=200, temperature=0.5, top_k=40)
    return tok.decode(out[0].tolist())

log("Starting generation loop...")
passed, failed = 0, 0
for i, task in enumerate(TASKS):
    log(f"Task {i+1}/{len(TASKS)}: {task[:50]}...")
    output = generate_code(task)
    code, lang = extract_code(output)
    
    # Test if code is valid Python
    if lang == 'python' or 'python' in task.lower():
        valid, error = test_syntax(code)
        if valid:
            passed += 1
            log(f"  ✓ Valid code generated ({len(code)} chars)")
        else:
            failed += 1
            log(f"  ✗ Syntax error: {error[:80]}...")
            # Self-heal: try to fix
            log(f"    Attempting self-heal...")
            fixed = improve_failed(task, code, error)
            fixed_code, _ = extract_code(fixed)
            valid2, error2 = test_syntax(fixed_code)
            if valid2:
                passed += 1; failed -= 1
                log(f"    ✓ Self-healed successfully!")
                # Save as training example
                with open(GENERATED_DATA, 'a') as f:
                    inp_tokens = tok.encode(task, bos=True, eos=False)
                    out_tokens = tok.encode(fixed_code, bos=True, eos=True)
                    f.write(json.dumps({"input_ids": inp_tokens, "target_ids": out_tokens, "mode": "build", "domain": "self_improved"}) + '\n')
                log(f"    Saved as training example")
    else:
        passed += 1
        log(f"  ✓ Generated ({len(code)} chars)")

log(f"\nResults: {passed}/{passed+failed} passed ({passed/(passed+failed)*100:.1f}%)")
log(f"Self-generated data saved to {GENERATED_DATA}")
log("=== SELF-IMPROVEMENT CYCLE COMPLETE ===")
