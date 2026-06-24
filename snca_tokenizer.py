import re, json
from pathlib import Path

class SNCATokenizer:
    def __init__(self, vocab_path=None, vocab_size=8192):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.inverse = {}
        self.special_tokens = {
            '<PAD>': 0, '<EOS>': 1, '<BOS>': 2, '<UNK>': 3,
            '<PLAN>': 4, '<EXECUTION>': 5, '<REFLECTION>': 6,
            '<TOOL_CALL>': 7, '<TOOL_RESULT>': 8, '<CITE>': 9, '<UNSURE>': 10,
            '<DECOMP>': 11, '<DISPATCH>': 12, '<SYNTH>': 13, '<SEP>': 14,
        }
        self.next_id = len(self.special_tokens)
        self._char_range = set()
        self._word_range = set()
        if vocab_path and Path(vocab_path).exists():
            self.load(vocab_path)
        else:
            self._build_base_vocab()

    def _build_base_vocab(self):
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.inverse[idx] = token

        ascii_start = self.next_id
        for i in range(32, 127):
            ch = chr(i)
            if ch not in self.vocab:
                self.vocab[ch] = self.next_id
                self.inverse[self.next_id] = ch
                self.next_id += 1
        ascii_end = self.next_id - 1
        self._char_range = set(range(ascii_start, ascii_end + 1))

        for i in range(100):
            num = str(i)
            if num not in self.vocab and self.next_id < self.vocab_size:
                self.vocab[num] = self.next_id
                self.inverse[self.next_id] = num
                self.next_id += 1

        common_tokens = [
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it',
            'for', 'not', 'on', 'with', 'as', 'this', 'but', 'from', 'or', 'by',
            'an', 'at', 'is', 'are', 'was', 'were', 'been', 'being', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'can', 'could', 'should', 'may', 'might',
            'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us',
            'my', 'your', 'his', 'its', 'our', 'their', 'what', 'which', 'who', 'whom',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'many',
            'some', 'any', 'no', 'none', 'other', 'more', 'most', 'such', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'also', 'well', 'now', 'then',
            'here', 'there', 'about', 'into', 'over', 'after', 'before', 'between', 'under', 'during',
            'up', 'down', 'out', 'off', 'away', 'back', 'within', 'without', 'through', 'across',
            'make', 'made', 'get', 'got', 'take', 'took', 'see', 'saw', 'know', 'knew',
            'think', 'thought', 'come', 'came', 'give', 'gave', 'find', 'found', 'tell', 'told',
            'use', 'used', 'need', 'want', 'work', 'look', 'call', 'try', 'ask', 'set',
            'show', 'move', 'keep', 'let', 'begin', 'start', 'end', 'help', 'turn', 'put',
            'write', 'read', 'speak', 'allow', 'seem', 'mean', 'follow', 'learn', 'change', 'play',
            'function', 'class', 'const', 'let', 'var', 'return', 'import', 'export', 'from', 'async',
            'await', 'def', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'raise',
            'finally', 'with', 'as', 'pass', 'break', 'continue', 'and', 'or', 'not', 'in',
            'is', 'true', 'false', 'null', 'none', 'self', 'super', 'yield', 'lambda', 'global',
            'div', 'span', 'button', 'input', 'form', 'style', 'className', 'onClick', 'onChange', 'onSubmit',
            'useState', 'useEffect', 'useRef', 'useContext', 'useReducer', 'useMemo', 'useCallback', 'useLayoutEffect',
            'render', 'default', 'props', 'state', 'children', 'component', 'element', 'react', 'reactdom',
            'query', 'fetch', 'then', 'catch', 'get', 'post', 'put', 'delete', 'patch',
            'url', 'uri', 'headers', 'params', 'body', 'json', 'status', 'error', 'success',
            'type', 'name', 'value', 'key', 'id', 'class', 'css', 'html', 'jsx', 'xml',
            'grid', 'flex', 'block', 'inline', 'margin', 'padding', 'width', 'height', 'color', 'size',
            'build', 'create', 'implement', 'define', 'handle', 'process', 'generate', 'parse', 'call', 'run',
            'test', 'check', 'verify', 'validate', 'accept', 'reject', 'request', 'response', 'data', 'code',
            'file', 'files', 'path', 'dir', 'list', 'sort', 'map', 'filter', 'reduce', 'find',
            'push', 'pop', 'shift', 'unshift', 'slice', 'splice', 'concat', 'join', 'split', 'trim',
            'index', 'length', 'count', 'match', 'search', 'replace', 'charAt', 'substring', 'includes', 'startsWith',
            'array', 'object', 'string', 'number', 'boolean', 'undefined', 'symbol', 'bigint', 'integer', 'float',
            'append', 'prepend', 'insert', 'remove', 'delete', 'update', 'select', 'insert', 'create', 'alter',
            'table', 'column', 'row', 'schema', 'index', 'key', 'primary', 'foreign', 'unique', 'constraint',
            'select', 'from', 'where', 'join', 'left', 'right', 'inner', 'outer', 'group', 'order',
            'server', 'client', 'api', 'route', 'middleware', 'handler', 'controller', 'model', 'view', 'template',
            'docker', 'container', 'image', 'volume', 'network', 'compose', 'dockerfile', 'kubernetes', 'pod', 'deployment',
            'config', 'env', 'secret', 'cert', 'token', 'auth', 'oauth', 'jwt', 'session', 'cookie',
            'encrypt', 'decrypt', 'hash', 'salt', 'password', 'login', 'logout', 'register', 'signup', 'signin',
            'hello', 'world', 'example', 'sample', 'demo', 'test', 'user', 'admin', 'guest', 'owner',
            'page', 'home', 'about', 'contact', 'footer', 'header', 'navbar', 'sidebar', 'main', 'content',
            'title', 'heading', 'paragraph', 'text', 'link', 'image', 'video', 'audio', 'icon', 'logo',
            'dark', 'light', 'theme', 'mode', 'primary', 'secondary', 'accent', 'background', 'foreground', 'border',
            'shadow', 'radius', 'opacity', 'transform', 'transition', 'animation', 'keyframe', 'scale', 'rotate', 'translate',
            'linux', 'windows', 'macos', 'android', 'ios', 'web', 'native', 'cross', 'platform', 'mobile',
            'message', 'channel', 'group', 'chat', 'send', 'receive', 'broadcast', 'emit', 'listen', 'connect',
            'debug', 'log', 'print', 'trace', 'profile', 'monitor', 'metric', 'alert', 'ticket', 'issue',
        ]
        word_start = self.next_id
        for token in common_tokens:
            if token not in self.vocab and self.next_id < self.vocab_size:
                self.vocab[token] = self.next_id
                self.inverse[self.next_id] = token
                self.next_id += 1
        self._word_range = set(range(word_start, self.next_id))

        while self.next_id < self.vocab_size:
            w = 'w' + str(self.next_id)
            self.vocab[w] = self.next_id
            self.inverse[self.next_id] = w
            self.next_id += 1
            self._word_range.add(self.next_id - 1)

    def encode(self, text, bos=True, eos=False):
        if not isinstance(text, str):
            text = str(text)
        ids = []
        if bos:
            ids.append(self.vocab.get('<BOS>', 2))

        tokens = re.findall(r'<[^>]+>|[A-Za-z_][A-Za-z0-9_]*|\d+|\S|\s', text)
        for token in tokens:
            if token.isspace():
                space_id = self.vocab.get(' ')
                if space_id is not None:
                    ids.append(space_id)
                continue
            if token in self.vocab:
                ids.append(self.vocab[token])
            elif token.lower() in self.vocab:
                ids.append(self.vocab[token.lower()])
            elif len(token) == 1:
                ids.append(self.vocab.get(token, self.vocab.get('<UNK>', 3)))
            else:
                for ch in token:
                    ids.append(self.vocab.get(ch, self.vocab.get('<UNK>', 3)))

        if eos:
            ids.append(self.vocab.get('<EOS>', 1))
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
                tokens.append('�')
        return ''.join(tokens)

    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump({'vocab': self.vocab, 'next_id': self.next_id}, f)

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
        self.vocab = data['vocab']
        self.next_id = data['next_id']
        self.inverse = {int(v): k for k, v in self.vocab.items()}
        self._char_range = set(i for i, t in self.inverse.items() if len(t) == 1 and not t.startswith('<'))
        self._word_range = set(i for i, t in self.inverse.items() if len(t) > 1 and not t.startswith('<'))

    @property
    def pad_id(self): return 0
    @property
    def eos_id(self): return 1
    @property
    def bos_id(self): return 2
    @property
    def unk_id(self): return 3

    @property
    def vocab_size_(self):
        return len(self.vocab)
