import torch
import numpy as np
import json
import time
import re
from pathlib import Path

PAD, EOS, BOS, PLAN, EXEC, REFLECT, TOOL_CALL, TOOL_RESULT, CITE, UNSURE = \
    0, 1, 2, 4, 5, 6, 7, 8, 9, 10

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class SNCA:
    def __init__(self, model_path=None, config_path='config/arch.json'):
        from snca_config import SNCACfg
        from snca_tokenizer import SNCATokenizer
        from keli_10k import Keli10KModel

        self.cfg = SNCACfg.load(config_path) if Path(config_path).exists() else SNCACfg()
        self.tokenizer = SNCATokenizer()

        print(f"Loading Keli10K model...")
        t0 = time.time()
        self.model = Keli10KModel(self.cfg)
        if model_path and Path(model_path).exists():
            self.model.load(model_path)
            print(f"  Checkpoint loaded: {model_path}")
        print(f"  Model ready in {time.time()-t0:.1f}s")

        self._init_memory()
        self._init_swarm()
        self._init_governor()
        self._init_personality()
        self._load_preseed()
        print("SNCA runtime ready.")

    def _init_memory(self):
        from core.l1_memory.memory_mesh import Hippocampus, ResonanceEngine, DreamEngine
        self.hippocampus = Hippocampus(dim=128, max_episodes=10000)
        self.resonance = ResonanceEngine(dim=128, n_bots=32)
        self.dream = DreamEngine(self.hippocampus, self.resonance)

    def _init_swarm(self):
        from core.l2_nanobot.bots import create_default_swarm
        self.swarm = create_default_swarm()

    def _init_governor(self):
        from core.l4_governor.governor import SovereignKernel, TruthEngine, SelfHealingLoop
        self.kernel = SovereignKernel()
        self.truth = TruthEngine()
        self.healer = SelfHealingLoop(self.kernel, self.swarm)

    def _init_personality(self):
        try:
            from keli_personality import RedForeman
            self.red_foreman = RedForeman(directness=0.9, sarcasm=0.6)
        except Exception:
            self.red_foreman = None

    def _load_preseed(self, pack_dir='preseed'):
        try:
            from preseed.package import PreseedPacker
            packer = PreseedPacker()
            count = packer.load_into_hippocampus(self.hippocampus, pack_dir)
            print(f"  Preseed: {count} docs loaded")
        except Exception as e:
            print(f"  Preseed: skipped ({e})")

    def chat(self, user_text):
        t0 = time.time()
        input_ids = self.tokenizer.encode(user_text, bos=True, eos=False)
        input_tensor = torch.tensor([input_ids], device=device)

        output_ids = self.model.generate(input_tensor, max_new=256, temperature=0.7, mode='plan')
        raw_output = self._decode(output_ids[0].tolist())
        generation_time = time.time() - t0

        citations = self._extract_citations(raw_output)
        has_unsure = '<UNSURE>' in raw_output

        response = raw_output
        if self.red_foreman:
            response = self.red_foreman.format(raw_output, {
                'phase': 'P4_synthesis',
                'is_error': not citations and not has_unsure,
            })

        return {
            'response': response,
            'citations': citations,
            'mode': 'plan',
            'unsure': has_unsure,
            'timing_ms': round(generation_time * 1000),
        }

    def build(self, task, existing_files=None):
        t0 = time.time()
        if existing_files is None:
            existing_files = {}

        territories = ['frontend', 'backend', 'data', 'devops']
        active_territories = self._select_territories(task)
        generated_files = {}

        for terr in active_territories:
            t_idx = territories.index(terr)
            prompt = task
            if existing_files:
                prompt += ' ' + ' '.join(existing_files.values())

            input_ids = self.tokenizer.encode(prompt, bos=True, eos=False)
            input_tensor = torch.tensor([input_ids], device=device)
            output_ids = self.model.generate(
                input_tensor, max_new=512, temperature=0.6,
                mode='build', territory_idx=t_idx,
            )
            raw_code = self._decode(output_ids[0].tolist())
            code = self._extract_code(raw_code)
            ext = self._ext_for(terr)
            fname = f"{terr}.{ext}"
            generated_files[fname] = code

        build_time = time.time() - t0
        return {
            'files': generated_files,
            'territories': active_territories,
            'mode': 'build',
            'timing_ms': round(build_time * 1000),
        }

    def idle(self):
        results = {}
        if self.dream:
            results['dream'] = self.dream.consolidate()
        if self.hippocampus:
            try:
                self.hippocampus.decay_step(hours_passed=1)
                results['decay'] = True
            except Exception:
                results['decay'] = False
        results['saved'] = False
        try:
            self.save_state('checkpoints/autosave.pt')
            results['saved'] = True
        except Exception:
            pass
        return results

    def save_state(self, path):
        state = {
            'model': self.model.model.state_dict(),
            'optimizer': self.model.optimizer.state_dict(),
            'hippocampus_episodes': self.hippocampus.episodes[:500],
            'hippocampus_index': [v.tolist() if hasattr(v, 'tolist') else v for v in self.hippocampus.index[:500]],
            'timestamp': time.time(),
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(state, path)
        print(f"State saved to {path}")

    def load_state(self, path):
        state = torch.load(path, map_location=device)
        self.model.model.load_state_dict(state['model'])
        self.model.optimizer.load_state_dict(state['optimizer'])
        self.hippocampus.episodes = state.get('hippocampus_episodes', [])
        self.hippocampus.index = [np.array(v, dtype=np.float32) for v in state.get('hippocampus_index', [])]
        print(f"State loaded from {path}")

    def _decode(self, ids):
        first_ascii = 32
        chars = []
        for i in ids:
            if i == PAD:
                continue
            if i == PLAN: chars.append('<PLAN>')
            elif i == EXEC: chars.append('<EXEC>')
            elif i == REFLECT: chars.append('<REFLECTION>')
            elif i == TOOL_CALL: chars.append('<TOOL_CALL>')
            elif i == TOOL_RESULT: chars.append('<TOOL_RESULT>')
            elif i == CITE: chars.append('<CITE>')
            elif i == UNSURE: chars.append('<UNSURE>')
            elif i == EOS: break
            elif first_ascii <= i < 128: chars.append(chr(i))
            elif i >= 128: chars.append(chr((i - 128) % 95 + 32))
            else: chars.append('?')
        return ''.join(chars)

    def _extract_citations(self, text):
        return re.findall(r'\[([^\]]+)\]\(https?://[^\)]+\)', text)

    def _select_territories(self, task):
        task_lower = task.lower()
        territories = []
        if any(w in task_lower for w in ['frontend', 'ui', 'react', 'css', 'html', 'component', 'dashboard', 'form', 'button', 'nav', 'modal', 'render', 'page']):
            territories.append('frontend')
        if any(w in task_lower for w in ['backend', 'api', 'server', 'express', 'route', 'middleware', 'auth', 'database', 'sql', 'mongo', 'endpoint']):
            territories.append('backend')
        if any(w in task_lower for w in ['data', 'pipeline', 'csv', 'etl', 'analytics', 'pandas', 'sql', 'transform', 'aggregate']):
            territories.append('data')
        if any(w in task_lower for w in ['devops', 'deploy', 'docker', 'ci', 'cd', 'pipeline', 'config', 'infra', 'terraform', 'kubernetes']):
            territories.append('devops')
        if not territories:
            territories = ['frontend', 'backend']
        return territories

    def _extract_code(self, text):
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[0].strip()
        lines = text.split('\n')
        start = 0
        for i, l in enumerate(lines):
            if l.strip().startswith(('def ', 'class ', 'function ', 'const ', 'let ', 'var ', 'import ', '<!DOCTYPE', '<html', '<div')):
                start = i
                break
        return '\n'.join(lines[start:]).strip()

    def _ext_for(self, territory):
        return {'frontend': 'jsx', 'backend': 'js', 'data': 'py', 'devops': 'yaml'}.get(territory, 'txt')


def create_snca(model_path=None, config_path='config/arch.json'):
    return SNCA(model_path=model_path, config_path=config_path)


if __name__ == '__main__':
    print("=== SNCA Runtime Backend API Test ===")
    snca = create_snca()

    if Path('checkpoints/swarm_best.pt').exists():
        snca.load_state('checkpoints/swarm_best.pt')

    print("\n--- chat() test ---")
    result = snca.chat("How do I manage state in React?")
    print(f"Response: {result['response'][:120]}...")
    print(f"Citations: {result['citations']}")
    print(f"Mode: {result['mode']}")
    print(f"Time: {result['timing_ms']}ms")

    print("\n--- build() test ---")
    result = snca.build("Create a React dashboard")
    print(f"Files: {list(result['files'].keys())}")
    print(f"Territories: {result['territories']}")

    print("\n--- idle() test ---")
    result = snca.idle()
    print(f"Results: {result}")

    print("\n--- save/load_state test ---")
    snca.save_state('/tmp/snca_test_state.pt')
    snca.load_state('/tmp/snca_test_state.pt')
    print("save/load cycle complete.")
