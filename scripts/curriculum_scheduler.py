import json
import random
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from advanced_trainer import AdvancedTrainer, load_jsonl


PHASES = [
    {
        "name": "frontend",
        "epochs": 3,
        "domains": ["frontend"],
        "target_acc": 0.80,
    },
    {
        "name": "backend",
        "epochs": 3,
        "domains": ["backend"],
        "target_acc": 0.80,
    },
    {
        "name": "design",
        "epochs": 2,
        "domains": ["design"],
        "target_acc": 0.80,
    },
    {
        "name": "fullstack",
        "epochs": 2,
        "domains": ["fullstack"],
        "target_acc": 0.75,
    },
    {
        "name": "debug",
        "epochs": 3,
        "domains": ["debug"],
        "target_acc": 0.85,
    },
    {
        "name": "nlp",
        "epochs": 2,
        "domains": ["nlp"],
        "target_acc": 0.85,
    },
    {
        "name": "mixed",
        "epochs": 5,
        "domains": ["frontend", "backend", "design", "fullstack", "debug", "nlp"],
        "target_acc": 0.90,
    },
]


def filter_by_domains(data, domains):
    return [d for d in data if d.get("domain", "") in domains]


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/advanced/train.jsonl')
    parser.add_argument('--val', default='data/advanced/val.jsonl')
    parser.add_argument('--resume', default=None)
    parser.add_argument('--start-phase', default=None)
    parser.add_argument('--checkpoint-dir', default='checkpoints')
    args = parser.parse_args()

    cfg = SNCACfg()
    tok = SNCATokenizer()

    print("=== CURRICULUM SCHEDULER ===")
    print(f"Loading data from {args.data}...")
    train_data = load_jsonl(args.data)
    val_data = load_jsonl(args.val)
    print(f"  Train: {len(train_data)} | Val: {len(val_data)}")

    domain_counts = defaultdict(int)
    for item in train_data:
        domain_counts[item.get("domain", "unknown")] += 1
    print("  Domains:", dict(domain_counts))

    start_phase = args.start_phase
    resumed = False
    trainer = None

    for phase in PHASES:
        if start_phase and phase["name"] != start_phase:
            if not resumed:
                continue
        if start_phase and phase["name"] == start_phase:
            resumed = True

        print(f"\n{'='*60}")
        print(f"PHASE: {phase['name'].upper()}")
        print(f"  Domains: {phase['domains']}")
        print(f"  Epochs: {phase['epochs']}")
        print(f"  Target Accuracy: {phase['target_acc']*100:.0f}%")
        print(f"{'='*60}")

        phase_train = filter_by_domains(train_data, phase["domains"])
        phase_val = filter_by_domains(val_data, phase["domains"])

        full_train = phase_train[:]
        if phase["name"] == "mixed":
            replay_count = len(phase_train) // len(phase["domains"])
            for dom in phase["domains"]:
                dom_data = filter_by_domains(train_data, [dom])
                replay = random.sample(dom_data, min(replay_count, len(dom_data)))
                full_train.extend(replay)

        random.shuffle(full_train)
        print(f"  Phase train: {len(full_train)} | Phase val: {len(phase_val)}")

        trainer = AdvancedTrainer(
            cfg, tok,
            lr=5e-4,
            batch_size=16,
            accum_steps=2,
            checkpoint_dir=args.checkpoint_dir,
        )

        if args.resume and not trainer.model:
            trainer.load_checkpoint(args.resume)
            args.resume = None

        trainer.train(
            full_train, phase_val,
            epochs=phase["epochs"],
            start_step=trainer.current_step if trainer else 0,
            phase_name=phase["name"],
        )

        checkpoint_path = f"{args.checkpoint_dir}/keli_phase_{phase['name']}.pt"
        trainer.save_checkpoint(checkpoint_path)

        if phase_val and trainer.history.get("val_acc"):
            best_acc = max(trainer.history["val_acc"])
            print(f"  Phase {phase['name']} best accuracy: {best_acc:.4f}")

        if phase["name"] == "mixed" and phase_val:
            if trainer.best_val_acc >= phase["target_acc"]:
                print(f"\nTARGET REACHED: {trainer.best_val_acc*100:.1f}% >= {phase['target_acc']*100:.0f}%")
            else:
                print(f"\nTarget not reached: {trainer.best_val_acc*100:.1f}% < {phase['target_acc']*100:.0f}%")
                print("Consider generating more data or extending training.")

    if trainer:
        trainer.save_checkpoint(f"{args.checkpoint_dir}/keli_90pct.pt")
        print(f"\nFinal model saved: {args.checkpoint_dir}/keli_90pct.pt")
        if trainer.history.get("val_acc"):
            print(f"Final best val accuracy: {max(trainer.history['val_acc'])*100:.1f}%")
    print("Curriculum complete.")


if __name__ == '__main__':
    main()
