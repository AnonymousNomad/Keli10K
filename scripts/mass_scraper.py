#!/usr/bin/env python3
"""Massive web scraper: collect 300K+ training examples from gold-standard sources."""
import sys, os, json, re, time, hashlib, random, html, threading, queue
from pathlib import Path
import urllib.request
import urllib.parse

sys.path.insert(0, '/tmp/opencode/snca')
from snca_tokenizer import SNCATokenizer

tok = SNCATokenizer()
BOS, EOS = 2, 1
OUT_DIR = '/tmp/opencode/snca/data/mass_web'
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

def t(text):
    return tok.encode(text, bos=False, eos=False)

def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; Kelibot/1.0)',
                'Accept': 'text/html,*/*',
            })
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode('utf-8', errors='replace')
        except Exception as e:
            if i < retries - 1:
                time.sleep(1)
    return None

def extract_text(html):
    if not html:
        return []
    for tag in ['script','style','nav','footer','noscript']:
        html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.DOTALL|re.IGNORECASE)
    for pat in [
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>',
        r'<div[^>]*class=["\'][^"\']*(?:content|documentation|prose|post|entry|body)[^"\']*["\'][^>]*>(.*?)</div>',
        r'<body[^>]*>(.*?)</body>',
    ]:
        m = re.search(pat, html, re.DOTALL|re.IGNORECASE)
        if m:
            html = m.group(1)
            break
    html = re.sub(r'<[^>]+>', ' ', html)
    html = html.replace('&nbsp;',' ').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
    html = re.sub(r'\s+', ' ', html)
    chunks = []
    for s in re.split(r'(?<=[.!?])\s+', html):
        s = s.strip()
        if 60 < len(s) < 1000:
            chunks.append(s)
        elif len(s) >= 1000:
            for sub in re.split(r'(?<=\.) ', s):
                if 60 < len(sub) < 1000:
                    chunks.append(sub)
    return chunks

def chunks_to_examples(chunks, source, domain):
    exs = []
    for chunk in chunks:
        inp = [BOS] + t(f"Learn about {source}:")[:32] + t(chunk[:200])[:128] + [14]
        tgt = [4] + t(chunk)[:512] + [EOS]
        exs.append({'input_ids': inp[:256], 'target_ids': tgt[:512], 'mode': 'plan', 'domain': domain, 'source': source})
    return exs

CODE_DOMAINS = {
    'python': 'backend', 'react': 'frontend', 'javascript': 'frontend',
    'html': 'frontend', 'css': 'design', 'fastapi': 'backend',
    'flask': 'backend', 'sql': 'backend', 'git': 'backend',
    'node': 'backend', 'typescript': 'frontend', 'api': 'backend',
}

# Massive URL list organized by source
URLS = {
    "python": {
        "base": "https://docs.python.org/3/",
        "pages": [
            "tutorial/introduction.html", "tutorial/controlflow.html",
            "tutorial/datastructures.html", "tutorial/modules.html",
            "tutorial/inputoutput.html", "tutorial/errors.html",
            "tutorial/classes.html", "tutorial/stdlib.html",
            "tutorial/stdlib2.html", "library/functions.html",
            "library/stdtypes.html", "library/exceptions.html",
            "library/os.html", "library/sys.html",
            "library/json.html", "library/re.html",
            "library/collections.html", "library/itertools.html",
            "library/functools.html", "library/pathlib.html",
            "library/datetime.html", "library/math.html",
            "library/random.html", "library/sqlite3.html",
            "library/http.html", "library/urllib.html",
            "library/subprocess.html", "library/tempfile.html",
            "library/logging.html", "library/configparser.html",
            "library/argparse.html", "library/threading.html",
            "library/asyncio.html", "library/typing.html",
            "howto/sorting.html", "howto/regex.html",
            "howto/logging.html", "howto/urllib2.html",
            "howto/argparse.html", "howto/asyncio.html",
        ]
    },
    "react": {
        "base": "https://react.dev/",
        "pages": [
            "reference/react", "reference/react/useState",
            "reference/react/useEffect", "reference/react/useContext",
            "reference/react/useReducer", "reference/react/useRef",
            "reference/react/useMemo", "reference/react/useCallback",
            "reference/react/useLayoutEffect", "reference/react/useImperativeHandle",
            "reference/react/useDeferredValue", "reference/react/useTransition",
            "reference/react/useId", "reference/react/useSyncExternalStore",
            "reference/react/useOptimistic", "reference/react/createContext",
            "reference/react/createRef", "reference/react/forwardRef",
            "reference/react/lazy", "reference/react/memo",
            "reference/react/Component", "reference/react/PureComponent",
            "reference/react/hooks", "reference/react/components",
            "reference/react-dom/components", "reference/react-dom/hooks",
            "learn/your-first-component", "learn/importing-and-exporting-components",
            "learn/writing-markup-with-jsx", "learn/javascript-in-jsx-with-curly-braces",
            "learn/passing-props-to-a-component", "learn/conditional-rendering",
            "learn/rendering-lists", "learn/responding-to-events",
            "learn/state-a-components-memory", "learn/render-and-commit",
            "learn/state-as-a-snapshot", "learn/queueing-a-series-of-state-updates",
            "learn/updating-objects-in-state", "learn/updating-arrays-in-state",
            "learn/managing-state", "learn/thinking-in-react",
        ]
    },
    "mdn_html": {
        "base": "https://developer.mozilla.org/en-US/docs/Web/HTML/",
        "pages": [
            "Element/html", "Element/head", "Element/body",
            "Element/div", "Element/span", "Element/p",
            "Element/h1", "Element/h2", "Element/h3", "Element/h4", "Element/h5", "Element/h6",
            "Element/ul", "Element/ol", "Element/li",
            "Element/table", "Element/thead", "Element/tbody", "Element/tr", "Element/th", "Element/td",
            "Element/form", "Element/input", "Element/button", "Element/select", "Element/textarea",
            "Element/label", "Element/fieldset", "Element/legend",
            "Element/a", "Element/img", "Element/video", "Element/audio",
            "Element/section", "Element/article", "Element/nav", "Element/header", "Element/footer",
            "Element/main", "Element/aside", "Element/figure", "Element/figcaption",
            "Element/script", "Element/style", "Element/link", "Element/meta",
            "Element/canvas", "Element/svg", "Element/iframe",
            "Element/details", "Element/summary", "Element/dialog",
            "Global_attributes", "Attributes",
            "Element/abbr", "Element/code", "Element/pre", "Element/blockquote",
            "Element/em", "Element/strong", "Element/small", "Element/mark",
            "Element/datalist", "Element/optgroup", "Element/option",
            "Element/progress", "Element/meter", "Element/output",
        ]
    },
    "mdn_css": {
        "base": "https://developer.mozilla.org/en-US/docs/Web/CSS/",
        "pages": [
            "display", "position", "flex", "grid", "float", "clear",
            "margin", "padding", "border", "outline", "box-shadow",
            "width", "height", "min-width", "max-width", "min-height", "max-height",
            "color", "background", "background-color", "background-image",
            "font", "font-size", "font-weight", "font-family", "line-height",
            "text-align", "text-decoration", "text-transform", "text-shadow",
            "overflow", "visibility", "opacity", "z-index",
            "transform", "transition", "animation", "keyframes",
            "flex-direction", "flex-wrap", "justify-content", "align-items", "gap",
            "grid-template-columns", "grid-template-rows", "grid-area",
            "media", "container",
            "cursor", "pointer-events", "user-select",
            "list-style", "content", "counter",
            "filter", "backdrop-filter", "clip-path",
            "var", "calc", "min", "max", "clamp",
            ":hover", ":focus", ":active", ":nth-child", ":before", ":after",
            "Specificity", "Cascade", "Inheritance",
        ]
    },
    "mdn_js": {
        "base": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/",
        "pages": [
            "Guide/Introduction", "Guide/Grammar_and_types",
            "Guide/Control_flow_and_error_handling", "Guide/Loops_and_iteration",
            "Guide/Functions", "Guide/Expressions_and_Operators",
            "Guide/Numbers_and_dates", "Guide/Text_formatting",
            "Guide/Regular_Expressions", "Guide/Indexed_collections",
            "Guide/Keyed_collections", "Guide/Working_with_objects",
            "Guide/Details_of_the_Object_Model", "Guide/Iterators_and_Generators",
            "Guide/Meta_programming", "Guide/Modules",
            "Reference/Global_Objects/Array", "Reference/Global_Objects/Object",
            "Reference/Global_Objects/String", "Reference/Global_Objects/Number",
            "Reference/Global_Objects/Boolean", "Reference/Global_Objects/Function",
            "Reference/Global_Objects/Promise", "Reference/Global_Objects/Map",
            "Reference/Global_Objects/Set", "Reference/Global_Objects/Date",
            "Reference/Global_Objects/Math", "Reference/Global_Objects/JSON",
            "Reference/Global_Objects/RegExp", "Reference/Global_Objects/Error",
            "Reference/Global_Objects/Symbol", "Reference/Global_Objects/WeakMap",
            "Reference/Global_Objects/Proxy", "Reference/Global_Objects/Reflect",
            "Reference/Operators", "Reference/Statements",
            "Reference/Functions", "Reference/Classes",
            "Reference/Functions/Arrow_functions", "Reference/Operators/Destructuring_assignment",
            "Reference/Operators/Spread_syntax", "Reference/Operators/Optional_chaining",
            "Reference/Operators/Nullish_coalescing",
            "Reference/Template_literals", "Reference/Strict_mode",
            "Reference/Global_Objects/Intl", "Reference/Global_Objects/Atomics",
            "Reference/Global_Objects/SharedArrayBuffer",
        ]
    },
}

def scrape_thread(source_name, urls, base_url, domain, results_queue):
    count = 0
    for page in urls:
        url = base_url + page
        html = fetch(url)
        if not html:
            continue
        chunks = extract_text(html)
        if not chunks:
            continue
        examples = chunks_to_examples(chunks, source_name, domain)
        # Save batch
        batch_path = f'{OUT_DIR}/{source_name}_{hashlib.md5(page.encode()).hexdigest()[:8]}.jsonl'
        with open(batch_path, 'w') as f:
            for ex in examples:
                f.write(json.dumps(ex) + '\n')
        count += len(examples)
        results_queue.put((source_name, page, len(examples)))
        time.sleep(0.5)
    results_queue.put((source_name, 'DONE', count))

def main():
    print("="*60)
    print("MASSIVE WEB DOCUMENTATION SCRAPER")
    print("Target: 300K+ training examples")
    print("="*60)

    results_queue = queue.Queue()
    threads = []

    for source_name, info in URLS.items():
        domain = CODE_DOMAINS.get(source_name.split('_')[0] if '_' in source_name else source_name, 'backend')
        # Handle prefixes
        if source_name.startswith('mdn_html'):
            domain = 'frontend'
        elif source_name.startswith('mdn_css'):
            domain = 'design'
        elif source_name.startswith('mdn_js'):
            domain = 'frontend'

        t = threading.Thread(target=scrape_thread, args=(source_name, info['pages'], info['base'], domain, results_queue))
        t.start()
        threads.append(t)

    total = 0
    completed = 0
    total_sources = len(URLS)

    while completed < total_sources:
        source, page, count = results_queue.get()
        if page == 'DONE':
            completed += 1
            print(f"  [{completed}/{total_sources}] {source}: {count} examples total")
        else:
            total += count

    for t in threads:
        t.join()

    # Combine all files
    all_data = []
    for f in Path(OUT_DIR).glob('*.jsonl'):
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    all_data.append(json.loads(line))

    random.shuffle(all_data)
    split = int(len(all_data) * 0.9)
    train = all_data[:split]
    val = all_data[split:]

    with open(f'{OUT_DIR}/train.jsonl', 'w') as f:
        for ex in train:
            f.write(json.dumps(ex) + '\n')
    with open(f'{OUT_DIR}/val.jsonl', 'w') as f:
        for ex in val:
            f.write(json.dumps(ex) + '\n')

    domain_counts = {}
    for ex in all_data:
        d = ex.get('domain', 'unknown')
        domain_counts[d] = domain_counts.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_data)} training examples from web docs")
    print(f"  Train: {len(train)} | Val: {len(val)}")
    print(f"  Domains: {json.dumps(domain_counts, indent=2)}")
    print(f"  Saved to {OUT_DIR}/")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
