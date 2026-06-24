import sys
import os
import json
import math
import torch
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from keli_10k import Keli10KModel
from trainer import SwarmDataset, collate_batch, compute_loss_and_acc

device = 'cuda' if torch.cuda.is_available() else 'cpu'


def load_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def evaluate_checkpoint(model_path, test_data, batch_size=16):
    cfg = SNCACfg()
    tok = SNCATokenizer()

    model = Keli10KModel(cfg)
    model.load(model_path)
    model.model.eval()
    print(f"Model loaded: {model_path}")
    print(f"  Parameters: {model.model.count_parameters()/1e6:.2f}M")

    dataset = SwarmDataset(test_data)
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=False, collate_fn=collate_batch
    )

    domain_metrics = defaultdict(lambda: {"loss": [], "acc": [], "count": 0})
    all_losses = []
    all_accs = []

    with torch.no_grad():
        for input_ids, mask, modes in loader:
            input_ids = input_ids.to(device)
            mask = mask.to(device)
            targets = input_ids.clone()
            targets[targets == 0] = -100

            is_build = all(m == 'build' for m in modes)
            logits, _ = model.model(input_ids, mode='build' if is_build else 'plan')
            loss, acc = compute_loss_and_acc(logits, targets, mask)

            batch_domains = [test_data[idx].get("domain", "unknown") for idx in range(
                sum(d["input_ids"] == list(input_ids[j].cpu().numpy()) for j, d in enumerate(test_data))
            )]

            all_losses.append(loss.item())
            all_accs.append(acc.item())

    overall_acc = sum(all_accs) / max(len(all_accs), 1)
    overall_loss = sum(all_losses) / max(len(all_losses), 1)
    overall_ppl = math.exp(min(overall_loss, 20))

    print(f"\n{'='*60}")
    print(f"OVERALL EVALUATION")
    print(f"{'='*60}")
    print(f"  Loss:       {overall_loss:.4f}")
    print(f"  Perplexity: {overall_ppl:.2f}")
    print(f"  Accuracy:   {overall_acc:.4f} ({overall_acc*100:.1f}%)")
    print(f"{'='*60}")

    domain_results = {}
    for domain, metrics in sorted(domain_metrics.items()):
        avg_loss = sum(metrics["loss"]) / max(metrics["count"], 1)
        avg_acc = sum(metrics["acc"]) / max(metrics["count"], 1)
        domain_results[domain] = {
            "samples": metrics["count"],
            "loss": avg_loss,
            "acc": avg_acc,
            "acc_pct": avg_acc * 100,
        }
        print(f"\n  {domain.upper():12s}: acc={avg_acc:.4f} ({avg_acc*100:.1f}%)  loss={avg_loss:.4f}  n={metrics['count']}")

    reached_90 = overall_acc >= 0.90
    print(f"\n{'='*60}")
    if reached_90:
        print(f"  TARGET REACHED: 90% overall accuracy!")
    else:
        print(f"  Target: 90%, current: {overall_acc*100:.1f}% (gap: {(0.90-overall_acc)*100:.1f}%)")
    print(f"{'='*60}")

    return {
        "overall": {
            "loss": overall_loss,
            "perplexity": overall_ppl,
            "accuracy": overall_acc,
            "accuracy_pct": overall_acc * 100,
            "target_reached": reached_90,
        },
        "domains": domain_results,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', default='checkpoints/keli_90pct.pt')
    parser.add_argument('--test', default='data/advanced/val.jsonl')
    parser.add_argument('--report', default='reports/final.json')
    parser.add_argument('--batch-size', type=int, default=16)
    args = parser.parse_args()

    print(f"Loading test data from {args.test}...")
    test_data = load_jsonl(args.test)
    print(f"  {len(test_data)} examples")

    results = evaluate_checkpoint(args.checkpoint, test_data, batch_size=args.batch_size)

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nReport saved to {args.report}")

    sys.exit(0 if results["overall"]["target_reached"] else 1)


if __name__ == '__main__':
    main()
