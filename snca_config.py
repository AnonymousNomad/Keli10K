from dataclasses import dataclass, asdict
import json

@dataclass
class SNCACfg:
    d_model: int = 384
    n_layers: int = 10
    n_heads: int = 6
    vocab_size: int = 8192
    max_len: int = 4096
    local_window: int = 128
    ffn_mult: int = 2
    dropout: float = 0.1
    d_ff: int = None

    special_tokens: tuple = (
        '<PAD>', '<EOS>', '<BOS>', '<PLAN>', '<EXECUTION>',
        '<REFLECTION>', '<TOOL_CALL>', '<TOOL_RESULT>', '<CITE>', '<UNSURE>'
    )

    def __post_init__(self):
        if self.d_ff is None:
            self.d_ff = self.d_model * self.ffn_mult
        if self.vocab_size < len(self.special_tokens):
            raise ValueError(f"vocab_size {self.vocab_size} must cover {len(self.special_tokens)} special tokens")

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            data = json.load(f)
        filtered = {}
        for k in cls.__dataclass_fields__:
            if k in data:
                filtered[k] = data[k]
        nested_l3 = data.get('layers', {}).get('l3_orchestrator', {})
        for k in ['d_model', 'n_layers', 'n_heads', 'vocab_size', 'max_seq_len', 'local_window', 'ffn_mult', 'dropout']:
            if k in nested_l3 and k not in filtered:
                v = nested_l3[k]
                if k == 'max_seq_len':
                    k = 'max_len'
                filtered[k] = v
        return cls(**filtered)

if __name__ == '__main__':
    cfg = SNCACfg()
    print(f"Config: d_model={cfg.d_model}, n_layers={cfg.n_layers}, n_heads={cfg.n_heads}")
    print(f"  d_ff={cfg.d_ff}, vocab={cfg.vocab_size}, max_len={cfg.max_len}")
