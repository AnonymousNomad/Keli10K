#!/usr/bin/env python3
"""Confidence scoring for Keli10K - knows what it doesn't know."""
import sys, os, json, math, torch
import torch.nn.functional as F

sys.path.insert(0, '/tmp/opencode/snca')
from keli_10k import Keli10KModel
from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer

device = 'cuda' if torch.cuda.is_available() else 'cpu'
tok = SNCATokenizer()
BOS, EOS, UNSURE_TOKEN = 2, 1, 10


def load_model(path):
    cfg = SNCACfg()
    model = Keli10KModel(cfg)
    model.load(path)
    model.model.eval()
    return model


def get_confidence(logits, top_k=5):
    """Compute confidence from logit distribution. Returns 0.0-1.0."""
    probs = F.softmax(logits, dim=-1)
    top_probs, top_indices = probs.topk(top_k, dim=-1)
    top1 = top_probs[..., 0]
    margin = top1 - top_probs[..., 1] if top_k > 1 else top1
    adjusted = top1 * (0.5 + 0.5 * margin.clamp(0, 1))
    return adjusted.mean().item()


def token_confidence(probs, top_k=3):
    """Per-token confidence analysis."""
    top_probs, top_indices = probs.topk(top_k, dim=-1)
    return {
        'top_token': int(top_indices[0].item()),
        'top_prob': float(top_probs[0].item()),
        'second_prob': float(top_probs[0, 1].item()) if top_k > 1 else 0,
        'margin': float((top_probs[0] - top_probs[0, 1]).item()) if top_k > 1 else float(top_probs[0].item()),
        'uncertain': top_probs[0].item() < 0.5,
        'gibberish': top_probs[0].item() < 0.05,
    }


def generate_with_confidence(model, prompt_text, max_tokens=256, temperature=0.7, min_confidence=0.0):
    """Generate text with per-token confidence tracking."""
    input_ids = torch.tensor([[BOS] + tok.encode(prompt_text, bos=False, eos=False) + [14]]).to(device)
    generated = input_ids[0].tolist()
    token_confidences = []
    unsure_triggered = False

    with torch.no_grad():
        for step in range(max_tokens):
            logits, _ = model.model(input_ids, mode='plan')
            next_logits = logits[0, -1, :] / temperature
            probs = F.softmax(next_logits, dim=-1)
            top_prob, next_token = probs.topk(1)

            conf = token_confidence(probs.unsqueeze(0))
            token_confidences.append(conf)

            # Check if we should output UNSURE
            if conf['uncertain'] and not unsure_triggered:
                if conf['top_prob'] < 0.3 and step > 5:
                    # Early in generation and very uncertain -> signal uncertainty
                    pass

            if conf['top_prob'] < 0.05:
                # Gibberish detection: if even the top token is very low prob
                generated.append(UNSURE_TOKEN)
                break

            if next_token.item() == EOS:
                break

            generated.append(next_token.item())
            input_ids = torch.cat([input_ids, next_token.unsqueeze(0).unsqueeze(0)], dim=1)
            if input_ids.size(1) > 1024:
                break

    text = tok.decode(generated, skip_special=True)
    avg_confidence = sum(c['top_prob'] for c in token_confidences) / len(token_confidences) if token_confidences else 0
    min_confidence_val = min(c['top_prob'] for c in token_confidences) if token_confidences else 0

    return {
        'text': text,
        'tokens': len(generated),
        'confidence': {
            'avg': avg_confidence,
            'min': min_confidence_val,
            'per_token': token_confidences[:10],  # First 10 for debug
        },
        'uncertain_regions': [i for i, c in enumerate(token_confidences) if c['uncertain']],
    }


def score_output(logits, target_ids, mask):
    """Score a complete output sequence against expected targets."""
    probs = F.softmax(logits, dim=-1)
    preds = logits.argmax(dim=-1)

    # Token accuracy
    shift_preds = preds[:, :-1]
    shift_targets = target_ids[:, 1:]
    shift_mask = mask[:, 1:]
    correct = (shift_preds == shift_targets) * shift_mask.bool()
    accuracy = correct.sum().float() / (shift_mask.sum() + 1e-8)

    # Confidence on correct vs incorrect tokens
    correct_conf = []
    incorrect_conf = []
    for i in range(shift_preds.size(0)):
        for j in range(shift_preds.size(1)):
            if shift_mask[i, j] > 0:
                conf = probs[i, j, shift_preds[i, j]].item()
                if shift_preds[i, j] == shift_targets[i, j]:
                    correct_conf.append(conf)
                else:
                    incorrect_conf.append(conf)

    avg_correct_conf = sum(correct_conf) / len(correct_conf) if correct_conf else 0
    avg_incorrect_conf = sum(incorrect_conf) / len(incorrect_conf) if incorrect_conf else 0

    return {
        'accuracy': accuracy.item(),
        'avg_confidence_correct': avg_correct_conf,
        'avg_confidence_incorrect': avg_incorrect_conf,
        'confidence_gap': avg_correct_conf - avg_incorrect_conf,
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', default='checkpoints/keli_best.pt')
    parser.add_argument('--prompt', default='How do I use useEffect?')
    parser.add_argument('--interactive', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    print(f"Loading model from {args.checkpoint}...")
    try:
        model = load_model(args.checkpoint)
        print(f"Model loaded ({model.model.count_parameters()/1e6:.2f}M params)")
    except Exception as e:
        print(f"Could not load model: {e}")
        print("Using random initialization instead")
        cfg = SNCACfg()
        model = Keli10KModel(cfg)
        model.model.eval()

    if args.test:
        test_prompts = [
            "How do I use useEffect?",
            "Build a todo app",
            "Fix this: const [todos] = useState()",
            "What is flexbox?",
            "Center a div with CSS",
            "Fetch API example with error handling",
            "React component with props",
            "SQL query for users table",
            "Explain closures in JavaScript",
            "Build a calculator app",
        ]
        for prompt in test_prompts:
            result = generate_with_confidence(model, prompt)
            c = result['confidence']
            marker = "✓" if c['avg'] > 0.5 else "?"
            print(f"\n{marker} [{c['avg']:.2f}] {prompt}")
            print(f"   {result['text'][:120]}{'...' if len(result['text']) > 120 else ''}")
    elif args.interactive:
        print("Interactive confidence demo. Type prompts or quit.")
        while True:
            prompt = input("\n> ").strip()
            if not prompt or prompt.lower() in ('quit', 'exit'):
                break
            result = generate_with_confidence(model, prompt)
            c = result['confidence']
            print(f"[conf={c['avg']:.2f} min={c['min']:.2f} unsure={len(result['uncertain_regions'])}]")
            print(result['text'][:200])
    else:
        result = generate_with_confidence(model, args.prompt)
        c = result['confidence']
        print(f"Prompt: {args.prompt}")
        print(f"Confidence: avg={c['avg']:.3f} min={c['min']:.3f}")
        print(f"Output: {result['text'][:200]}")
