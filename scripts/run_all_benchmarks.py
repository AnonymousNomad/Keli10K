import sys, os, json, torch, math, time, re
from pathlib import Path
sys.path.insert(0, '/tmp/opencode/snca')
sys.path.insert(0, '/tmp/opencode/snca/scripts')

from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from keli_10k import Keli10K
from trainer import compute_loss_and_acc, collate_batch
from torch.utils.data import DataLoader
from trainer import SwarmDataset

PAD = 0
BENCHMARKS = {}

def load_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line: data.append(json.loads(line))
    return data

def decode(ids):
    first_ascii = 32
    chars = []
    for i in ids:
        if i in (0, 1, 2): continue
        if i == 4: chars.append('<PLAN>')
        elif i == 5: chars.append('<EXEC>')
        elif i == 6: chars.append('<REFLECTION>')
        elif i == 7: chars.append('<TOOL_CALL>')
        elif i == 8: chars.append('<TOOL_RESULT>')
        elif i == 9: chars.append('<CITE>')
        elif i == 10: chars.append('<UNSURE>')
        elif first_ascii <= i < 128: chars.append(chr(i))
        elif i >= 128:
            m = (i - 128) % 95 + 32
            chars.append(chr(m))
        else: chars.append('?')
    return ''.join(chars)

# ═══════════════════════════════════════════════════════
# BENCHMARK 1: Accuracy on validation data (per-domain)
# ═══════════════════════════════════════════════════════
def bench_accuracy(model, val_data, batch_size=16):
    print("\n═══════════════════════════════════════════")
    print("BENCHMARK 1: ACCURACY EVALUATION")
    print("═══════════════════════════════════════════")
    ds = SwarmDataset(val_data)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, collate_fn=collate_batch)
    
    domain_items = {}
    for item in val_data:
        d = item.get('domain', 'unknown')
        if d not in domain_items: domain_items[d] = []
        domain_items[d].append(item)
    
    all_loss, all_acc = [], []
    domain_results = {}
    
    model.eval()
    with torch.no_grad():
        for input_ids, mask, modes in loader:
            targets = input_ids.clone()
            targets[targets == PAD] = -100
            is_build = all(m == 'build' for m in modes)
            logits, _ = model(input_ids, mode='build' if is_build else 'plan')
            loss, acc = compute_loss_and_acc(logits, targets, mask)
            all_loss.append(loss.item())
            all_acc.append(acc.item())
    
    overall_loss = sum(all_loss) / max(len(all_loss), 1)
    overall_acc = sum(all_acc) / max(len(all_acc), 1)
    overall_ppl = math.exp(min(overall_loss, 20))
    
    print(f"\n  OVERALL:")
    print(f"    Loss:       {overall_loss:.4f}")
    print(f"    Perplexity: {overall_ppl:.2f}")
    print(f"    Accuracy:   {overall_acc:.4f} ({overall_acc*100:.2f}%)")
    print(f"    90% Target: {'✓ REACHED' if overall_acc >= 0.90 else '✗ NOT YET'}")
    
    # Per-domain
    for domain, items in sorted(domain_items.items()):
        d_ds = SwarmDataset(items)
        if len(d_ds) == 0: continue
        d_loader = DataLoader(d_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_batch)
        d_loss, d_acc = [], []
        with torch.no_grad():
            for input_ids, mask, modes in d_loader:
                targets = input_ids.clone()
                targets[targets == PAD] = -100
                is_build = all(m == 'build' for m in modes)
                logits, _ = model(input_ids, mode='build' if is_build else 'plan')
                loss, acc = compute_loss_and_acc(logits, targets, mask)
                d_loss.append(loss.item())
                d_acc.append(acc.item())
        avg_loss = sum(d_loss) / max(len(d_loss), 1)
        avg_acc = sum(d_acc) / max(len(d_acc), 1)
        domain_results[domain] = {"loss": avg_loss, "acc": avg_acc, "samples": len(items)}
        print(f"    {domain:15s}: acc={avg_acc*100:6.2f}%  loss={avg_loss:.4f}  n={len(items)}")
    
    result = {"loss": overall_loss, "perplexity": overall_ppl, "accuracy": overall_acc, "accuracy_pct": overall_acc*100, "target_90_reached": overall_acc >= 0.90, "domains": domain_results}
    BENCHMARKS["accuracy"] = result
    return result

# ═══════════════════════════════════════════════════════
# BENCHMARK 2: Generation Quality
# ═══════════════════════════════════════════════════════
def bench_generation(model, tok):
    print("\n═══════════════════════════════════════════")
    print("BENCHMARK 2: GENERATION QUALITY")
    print("═══════════════════════════════════════════")
    
    plan_prompts = [
        "Write a Python function to sort a list of numbers",
        "Explain how HTTP requests work",
        "What is the difference between SQL and NoSQL?",
        "How does CSS Flexbox work?",
        "Write a function that finds duplicates in an array",
    ]
    build_prompts = [
        "Build a React counter component",
        "Create an HTML form with validation",
        "Write a Python API endpoint",
    ]
    
    results = {"plan_mode": [], "build_mode": [], "overall_pass_rate": 0}
    passed, total = 0, 0
    
    for prompt in plan_prompts:
        ids = tok.encode(prompt, bos=True, eos=False)
        inp = torch.tensor([ids], dtype=torch.long)
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(inp, max_new=80, temperature=0.7, top_k=40)
        elapsed = time.time() - t0
        decoded = decode(out[0].tolist())
        has_plan_tag = '<PLAN>' in decoded
        has_exec_tag = '<EXEC>' in decoded
        has_code = bool(re.search(r'(def |function|const |let |var |class |import|from )', decoded))
        is_coherent = len(decoded) > 20
        p = has_plan_tag or has_exec_tag or has_code
        if p: passed += 1
        total += 1
        results["plan_mode"].append({"prompt": prompt[:50], "has_tags": has_plan_tag or has_exec_tag, "has_code": has_code, "coherent": is_coherent, "time": f"{elapsed:.1f}s", "preview": decoded[:100]})
        print(f"  {'PASS' if p else 'FAIL'} plan: {prompt[:40]}... -> {decoded[:80]}...")
    
    for prompt in build_prompts:
        ids = tok.encode(prompt, bos=True, eos=False)
        inp = torch.tensor([ids], dtype=torch.long)
        t0 = time.time()
        with torch.no_grad():
            out = model.generate(inp, max_new=80, temperature=0.7, top_k=40, mode='build')
        elapsed = time.time() - t0
        decoded = decode(out[0].tolist())
        has_code = bool(re.search(r'(def |function|const |let |var |<[a-z]|class |import)', decoded))
        is_coherent = len(decoded) > 20
        p = has_code and is_coherent
        if p: passed += 1
        total += 1
        results["build_mode"].append({"prompt": prompt[:50], "has_tags": True, "has_code": has_code, "coherent": is_coherent, "time": f"{elapsed:.1f}s", "preview": decoded[:100]})
        print(f"  {'PASS' if p else 'FAIL'} build: {prompt[:40]}... -> {decoded[:80]}...")
    
    rate = passed / max(total, 1)
    results["overall_pass_rate"] = rate
    BENCHMARKS["generation"] = results
    print(f"\n  Generation pass rate: {passed}/{total} = {rate*100:.1f}%")
    return results

# ═══════════════════════════════════════════════════════
# BENCHMARK 3: Perplexity & Loss Stability
# ═══════════════════════════════════════════════════════
def bench_perplexity(model, val_data, tok):
    print("\n═══════════════════════════════════════════")
    print("BENCHMARK 3: PERPLEXITY & LOSS STABILITY")
    print("═══════════════════════════════════════════")
    
    ds = SwarmDataset(val_data)
    loader = DataLoader(ds, batch_size=32, shuffle=False, collate_fn=collate_batch)
    
    all_ppl = []
    model.eval()
    with torch.no_grad():
        for input_ids, mask, modes in loader:
            targets = input_ids.clone()
            targets[targets == PAD] = -100
            is_build = all(m == 'build' for m in modes)
            logits, _ = model(input_ids, mode='build' if is_build else 'plan')
            loss, acc = compute_loss_and_acc(logits, targets, mask)
            ppl = math.exp(min(loss.item(), 20))
            all_ppl.append(ppl)
    
    avg_ppl = sum(all_ppl) / max(len(all_ppl), 1)
    min_ppl = min(all_ppl)
    max_ppl = max(all_ppl)
    std_ppl = (sum((p - avg_ppl)**2 for p in all_ppl) / max(len(all_ppl), 1)) ** 0.5
    
    result = {"avg_perplexity": avg_ppl, "min_perplexity": min_ppl, "max_perplexity": max_ppl, "perplexity_std": std_ppl, "stability": "stable" if std_ppl < 1.0 else "unstable"}
    BENCHMARKS["perplexity"] = result
    print(f"  Avg Perplexity: {avg_ppl:.4f}")
    print(f"  Min/Max: {min_ppl:.4f} / {max_ppl:.4f}")
    print(f"  Std Dev: {std_ppl:.4f}")
    print(f"  Stability: {result['stability']}")
    return result

# ═══════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════
def main():
    print("\n" + "█" * 60)
    print("█  KELI10K PROFESSIONAL BENCHMARK SUITE")
    print("█" * 60)
    
    cfg = SNCACfg()
    tok = SNCATokenizer()
    
    ckpt = torch.load('checkpoints/keli_navy_latest.pt', map_location='cpu')
    n_bots = ckpt['model_state']['nanobot_embed.weight'].shape[0]
    step = ckpt.get('step', '?')
    loss_val = ckpt.get('loss', ckpt.get('best_loss', None))
    
    model = Keli10K(
        vocab_size=cfg.vocab_size, dim=cfg.d_model,
        n_heads=cfg.n_heads, n_layers=cfg.n_layers,
        ffn_hidden=cfg.d_ff, max_len=cfg.max_len,
        n_nanobots=n_bots, nanobot_dim=200,
        n_comm_rounds=5, dropout=cfg.dropout,
    )
    model.load_state_dict(ckpt['model_state'], strict=True)
    model.eval()
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n  Model: Keli10K Navy")
    print(f"  Parameters: {total_params/1e6:.2f}M")
    print(f"  Nanobots: {n_bots:,}")
    print(f"  Training Step: {step}")
    if loss_val:
        print(f"  Training Loss: {float(loss_val):.6f}")
    print(f"  Tokenizer Vocab: {cfg.vocab_size}")
    print(f"  Max Context: {cfg.max_len}")
    
    # Load data
    val_data = load_jsonl('data/advanced/val.jsonl')
    print(f"\n  Validation Data: {len(val_data)} examples")
    
    # Run benchmarks
    bench_accuracy(model, val_data)
    bench_generation(model, tok)
    bench_perplexity(model, val_data, tok)
    
    # Summary
    print("\n" + "═" * 60)
    print("BENCHMARK SUMMARY")
    print("═" * 60)
    acc = BENCHMARKS.get("accuracy", {})
    gen = BENCHMARKS.get("generation", {})
    ppl = BENCHMARKS.get("perplexity", {})
    
    print(f"  Overall Accuracy:    {acc.get('accuracy_pct', 0):.2f}%")
    print(f"  90% Target Reached: {'✓ YES' if acc.get('target_90_reached') else '✗ NO'}")
    print(f"  Generation Pass:     {gen.get('overall_pass_rate', 0)*100:.1f}%")
    print(f"  Avg Perplexity:      {ppl.get('avg_perplexity', 0):.4f}")
    print(f"  Perplexity Stability: {ppl.get('stability', 'N/A')}")
    
    if acc.get('target_90_reached'):
        print(f"\n  ★ MODEL BENCHMARK-READY: 90% accuracy target achieved!")
    else:
        gap = 90 - acc.get('accuracy_pct', 0)
        print(f"\n  Training gap to 90%: {gap:.2f}% — continuing training...")
    
    # Save report
    report = {
        "model": {"type": "Keli10K-Navy", "parameters": total_params, "nanobots": n_bots, "step": step, "training_loss": float(loss_val) if loss_val else None},
        "benchmarks": BENCHMARKS,
        "summary": {"accuracy_pct": acc.get('accuracy_pct', 0), "target_90_reached": acc.get('target_90_reached', False), "generation_pass_rate": gen.get('overall_pass_rate', 0), "avg_perplexity": ppl.get('avg_perplexity', 0), "timestamp": time.time()},
    }
    with open('eval_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n  Full report saved to eval_report.json")
    print(f"\n")
    
    return report

if __name__ == '__main__':
    main()
