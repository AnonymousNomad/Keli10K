#!/usr/bin/env python3
"""Launch training as a proper daemon process."""
import os, sys, time

PID_FILE = '/tmp/keli_train.pid'
LOG_FILE = '/tmp/opencode/snca/training_curriculum.log'


def daemonize():
    pid = os.fork()
    if pid > 0:
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
        print(f"Training daemon started (PID {pid})")
        print(f"Log: {LOG_FILE}")
        print(f"Monitor: tail -f {LOG_FILE}")
        sys.exit(0)
    os.setsid()
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    os.chdir('/tmp/opencode/snca')
    sys.stdout = open(LOG_FILE, 'w')
    sys.stderr = sys.stdout
    return


def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


if __name__ == '__main__':
    daemonize()
    log("Daemon initializing...")

    try:
        sys.path.insert(0, '/tmp/opencode/snca')
        sys.path.insert(0, '/tmp/opencode/snca/scripts')

        log("Loading modules...")
        from advanced_trainer import AdvancedTrainer, load_jsonl
        from snca_config import SNCACfg
        from snca_tokenizer import SNCATokenizer

        cfg = SNCACfg()
        tok = SNCATokenizer()
        log("Loading training data...")
        train_data = load_jsonl('data/advanced/train.jsonl')
        val_data = load_jsonl('data/advanced/val.jsonl')
        log(f"Loaded {len(train_data)} train / {len(val_data)} val")

        trainer = AdvancedTrainer(cfg, tok, lr=5e-4, batch_size=8, accum_steps=4, checkpoint_dir='checkpoints')

        phases = [
            ('frontend', 3), ('backend', 3), ('design', 2),
            ('fullstack', 2), ('debug', 3), ('nlp', 2), ('mixed', 3),
        ]

        for phase_name, epochs in phases:
            log(f"Starting phase: {phase_name} ({epochs} epochs)")
            phase_train = [d for d in train_data if d.get('domain', '') == phase_name or phase_name == 'mixed']
            phase_val = [d for d in val_data if d.get('domain', '') == phase_name or phase_name == 'mixed']
            log(f"  Train: {len(phase_train)} | Val: {len(phase_val)}")

            if phase_name == 'mixed':
                from collections import defaultdict
                dc = defaultdict(list)
                for d in train_data:
                    dc[d.get('domain', 'unknown')].append(d)
                phase_train = []
                for dom, samples in dc.items():
                    phase_train.extend(samples[:len(samples) // 6 * 2])
                import random
                random.shuffle(phase_train)
                phase_val = val_data
                log(f"  Mixed mode: {len(phase_train)} training samples")

            trainer.train(phase_train, phase_val, epochs=epochs, phase_name=phase_name)
            ckpt = f'checkpoints/keli_phase_{phase_name}.pt'
            trainer.save_checkpoint(ckpt)
            log(f"Phase {phase_name} complete, saved to {ckpt}")

        trainer.save_checkpoint('checkpoints/keli_final.pt')
        if trainer.history.get('val_acc'):
            best = max(trainer.history['val_acc'])
            log(f"CURRICULUM COMPLETE! Best val acc: {best:.4f} ({best*100:.1f}%)")
        else:
            log("Curriculum complete (no val acc tracked)")

    except Exception as e:
        import traceback
        log(f"FATAL ERROR: {e}")
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
