import sys
import os
import torch
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snca_config import SNCACfg
from snca_tokenizer import SNCATokenizer
from keli_10k import Keli10KModel


def export_to_onnx(model, output_path, vocab_size=8192, seq_len=512):
    dummy_input = torch.randint(0, vocab_size, (1, seq_len))
    torch.onnx.export(
        model.model,
        dummy_input,
        output_path,
        input_names=['input_ids'],
        output_names=['logits', 'aux'],
        dynamic_axes={'input_ids': {0: 'batch', 1: 'sequence'}, 'logits': {0: 'batch', 1: 'sequence'}},
        opset_version=14,
    )
    print(f"ONNX exported: {output_path}")


def quantize_int8(model, output_path):
    quantized = torch.quantization.quantize_dynamic(
        model.model, {torch.nn.Linear}, dtype=torch.qint8
    )
    torch.save(quantized.state_dict(), output_path)
    print(f"INT8 quantized: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='checkpoints/keli_90pct.pt')
    parser.add_argument('--output-dir', default='exports')
    parser.add_argument('--quantize', choices=['int8', 'onnx', 'both'], default='both')
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    cfg = SNCACfg()

    print(f"Loading model from {args.input}...")
    model = Keli10KModel(cfg)
    model.load(args.input)
    print(f"Model loaded: {model.model.count_parameters()/1e6:.2f}M")

    base = Path(args.input).stem

    if args.quantize in ('onnx', 'both'):
        onnx_path = f"{args.output_dir}/{base}.onnx"
        export_to_onnx(model, onnx_path)

    if args.quantize in ('int8', 'both'):
        int8_path = f"{args.output_dir}/{base}_int8.pt"
        quantize_int8(model, int8_path)

    print(f"Export complete. Files in {args.output_dir}/")
    original_size = os.path.getsize(args.input)
    for f in Path(args.output_dir).iterdir():
        if f.is_file():
            ratio = f.stat().st_size / original_size if original_size else 1
            print(f"  {f.name}: {f.stat().st_size / 1024 / 1024:.1f}MB (ratio: {ratio:.2f})")


if __name__ == '__main__':
    main()
