import json
import re
from pathlib import Path

class SNCATokenizer:
    def __init__(self, vocab_path=None, vocab_size=8192):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.inverse = {}
        self.special_tokens = {
            '<PAD>': 0, '<UNK>': 1, '<BOS>': 2, '<EOS>': 3,
            '<SEP>': 4, '<CLS>': 5, '<MASK>': 6,
            '<DECOMP>': 7, '<DISPATCH>': 8, '<SYNTH>': 9, '<CITE>': 10,
            '<BOT>': 11, '<QUERY>': 12, '<RESULT>': 13, '<CONFLICT>': 14
        }
        self.next_id = len(self.special_tokens)
        if vocab_path and Path(vocab_path).exists():
            self.load(vocab_path)
        else:
            self._build_base_vocab()

    def _build_base_vocab(self):
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.inverse[idx] = token

        for i in range(128, 256):
            ch = bytes([i]).decode('latin-1')
            if ch.isprintable() or ch in '\n\r\t':
                self.vocab[ch] = self.next_id
                self.inverse[self.next_id] = ch
                self.next_id += 1

        common_tokens = [
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it',
            'for', 'not', 'on', 'with', 'as', 'this', 'but', 'from', 'or', 'by',
            'an', 'at', 'is', 'are', 'was', 'were', 'been', 'being', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'can', 'could', 'should', 'may', 'might',
            'function', 'class', 'const', 'let', 'var', 'return', 'import', 'export', 'from', 'async',
            'await', 'def', 'if', 'else', 'for', 'while', 'try', 'catch', 'throw', 'new',
            'true', 'false', 'null', 'undefined', 'None', 'True', 'False', 'self', 'this', 'typeof',
            'then', 'map', 'filter', 'reduce', 'forEach', 'push', 'pop', 'shift', 'unshift', 'length',
            'div', 'span', 'button', 'input', 'form', 'style', 'className', 'onClick', 'useState', 'useEffect',
            'render', 'return', 'export', 'default', 'props', 'state', 'setState', 'Component', 'React', 'import',
            'query', 'fetch', 'get', 'post', 'put', 'delete', 'patch', 'url', 'headers', 'body',
            'css', 'html', 'jsx', 'tsx', 'json', 'xml', 'svg', 'png', 'jpg', 'gif',
            'error', 'success', 'status', 'type', 'name', 'value', 'key', 'id', 'class', 'data'
        ]

        for token in common_tokens:
            if token not in self.vocab and self.next_id < self.vocab_size:
                self.vocab[token] = self.next_id
                self.inverse[self.next_id] = token
                self.next_id += 1

        digits = [str(i) for i in range(100)]
        for d in digits:
            if d not in self.vocab and self.next_id < self.vocab_size:
                self.vocab[d] = self.next_id
                self.inverse[self.next_id] = d
                self.next_id += 1

        while self.next_id < self.vocab_size:
            remaining = self.vocab_size - self.next_id
            if remaining > 2:
                self.vocab['w' + str(self.next_id)] = self.next_id
                self.inverse[self.next_id] = 'w' + str(self.next_id)
            self.next_id += 1

    def encode(self, text, add_special=True):
        text = str(text)
        ids = []
        if add_special:
            ids.append(self.special_tokens['<BOS>'])

        words = re.findall(r'\w+|<[^>]+>|[^\w\s]|\s+', text)
        for word in words:
            if word in self.vocab:
                ids.append(self.vocab[word])
            else:
                lower = word.lower()
                if lower in self.vocab:
                    ids.append(self.vocab[lower])
                else:
                    ids.append(self.special_tokens['<UNK>'])

        if add_special:
            ids.append(self.special_tokens['<EOS>'])
        return ids

    def decode(self, ids, skip_special=False):
        tokens = []
        for i in ids:
            if i in self.inverse:
                tok = self.inverse[i]
                if skip_special and tok.startswith('<') and tok.endswith('>'):
                    continue
                tokens.append(tok)
            else:
                tokens.append('<UNK>')
        return ''.join(tokens)

    def save(self, path):
        with open(path, 'w') as f:
            json.dump({'vocab': self.vocab, 'next_id': self.next_id}, f)
        print(f"  Tokenizer saved to {path}")

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
            self.vocab = data['vocab']
            self.next_id = data.get('next_id', len(self.vocab))
            self.inverse = {v: k for k, v in self.vocab.items()}
        print(f"  Tokenizer loaded from {path} ({len(self.vocab)} tokens)")

    @property
    def pad_id(self): return self.special_tokens['<PAD>']

    @property
    def bos_id(self): return self.special_tokens['<BOS>']

    @property
    def eos_id(self): return self.special_tokens['<EOS>']

    @property
    def unk_id(self): return self.special_tokens['<UNK>']
