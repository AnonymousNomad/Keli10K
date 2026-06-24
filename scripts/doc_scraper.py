#!/usr/bin/env python3
"""Scrape gold-standard documentation from the web and generate training data."""

import sys, os, json, re, time, hashlib, random, html
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

sys.path.insert(0, '/tmp/opencode/snca')
from snca_tokenizer import SNCATokenizer

tok = SNCATokenizer()
BOS, EOS, PAD = 2, 1, 0

def t(text):
    return tok.encode(text, bos=False, eos=False)

OUT_DIR = '/tmp/opencode/snca/data/web_docs'
Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

# ============================================================
# GOLD-STANDARD DOCUMENTATION SOURCES
# ============================================================

SOURCES = {
    "python": {
        "url": "https://docs.python.org/3/tutorial/index.html",
        "pages": [
            "https://docs.python.org/3/tutorial/introduction.html",
            "https://docs.python.org/3/tutorial/controlflow.html",
            "https://docs.python.org/3/tutorial/datastructures.html",
            "https://docs.python.org/3/tutorial/modules.html",
            "https://docs.python.org/3/tutorial/inputoutput.html",
            "https://docs.python.org/3/tutorial/errors.html",
            "https://docs.python.org/3/tutorial/classes.html",
            "https://docs.python.org/3/tutorial/stdlib.html",
            "https://docs.python.org/3/library/functions.html",
            "https://docs.python.org/3/library/stdtypes.html",
        ]
    },
    "react": {
        "url": "https://react.dev/reference/react",
        "pages": [
            "https://react.dev/reference/react/useState",
            "https://react.dev/reference/react/useEffect",
            "https://react.dev/reference/react/useContext",
            "https://react.dev/reference/react/useReducer",
            "https://react.dev/reference/react/useRef",
            "https://react.dev/reference/react/useMemo",
            "https://react.dev/reference/react/useCallback",
            "https://react.dev/reference/react/createContext",
            "https://react.dev/reference/react/Component",
            "https://react.dev/learn/your-first-component",
        ]
    },
    "mdn_html": {
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTML",
        "pages": [
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/html",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/section",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/nav",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/header",
            "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/footer",
        ]
    },
    "mdn_css": {
        "url": "https://developer.mozilla.org/en-US/docs/Web/CSS",
        "pages": [
            "https://developer.mozilla.org/en-US/docs/Web/CSS/display",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/flex",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/grid",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/position",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/animation",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/transition",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/media",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/transform",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/box-shadow",
            "https://developer.mozilla.org/en-US/docs/Web/CSS/background",
        ]
    },
    "mdn_js": {
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "pages": [
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Functions",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Control_flow_and_error_handling",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Loops_and_iteration",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/async_function",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes",
            "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON",
            "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API",
            "https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API",
        ]
    },
    "fastapi": {
        "url": "https://fastapi.tiangolo.com",
        "pages": [
            "https://fastapi.tiangolo.com/tutorial/first-steps/",
            "https://fastapi.tiangolo.com/tutorial/path-params/",
            "https://fastapi.tiangolo.com/tutorial/query-params/",
            "https://fastapi.tiangolo.com/tutorial/body/",
            "https://fastapi.tiangolo.com/tutorial/response-model/",
            "https://fastapi.tiangolo.com/tutorial/security/",
            "https://fastapi.tiangolo.com/tutorial/middleware/",
            "https://fastapi.tiangolo.com/tutorial/cors/",
            "https://fastapi.tiangolo.com/tutorial/sql-databases/",
            "https://fastapi.tiangolo.com/tutorial/testing/",
        ]
    },
    "flask": {
        "url": "https://flask.palletsprojects.com",
        "pages": [
            "https://flask.palletsprojects.com/en/stable/quickstart/",
            "https://flask.palletsprojects.com/en/stable/tutorial/",
            "https://flask.palletsprojects.com/en/stable/patterns/",
            "https://flask.palletsprojects.com/en/stable/api/",
        ]
    },
    "sqlite": {
        "url": "https://sqlite.org/docs.html",
        "pages": [
            "https://sqlite.org/lang_select.html",
            "https://sqlite.org/lang_insert.html",
            "https://sqlite.org/lang_update.html",
            "https://sqlite.org/lang_delete.html",
            "https://sqlite.org/lang_createtable.html",
            "https://sqlite.org/foreignkeys.html",
            "https://sqlite.org/lang_aggfunc.html",
            "https://sqlite.org/datatype3.html",
        ]
    },
    "git": {
        "url": "https://git-scm.com/doc",
        "pages": [
            "https://git-scm.com/docs/git-add",
            "https://git-scm.com/docs/git-commit",
            "https://git-scm.com/docs/git-branch",
            "https://git-scm.com/docs/git-merge",
            "https://git-scm.com/docs/git-rebase",
            "https://git-scm.com/docs/git-push",
            "https://git-scm.com/docs/git-pull",
            "https://git-scm.com/docs/git-log",
        ]
    },
    "design": {
        "url": "https://web.dev/learn/design/",
        "pages": [
            "https://web.dev/learn/design/responsive/",
            "https://web.dev/learn/design/typography/",
            "https://web.dev/learn/design/color/",
            "https://web.dev/learn/design/layout/",
            "https://web.dev/learn/design/navigation/",
            "https://web.dev/learn/design/media/",
            "https://web.dev/learn/design/accessibility/",
            "https://web.dev/learn/design/interaction/",
        ]
    },
    "nodejs": {
        "url": "https://nodejs.org/en/docs/guides",
        "pages": [
            "https://nodejs.org/en/docs/guides/getting-started-guide",
            "https://nodejs.org/en/docs/guides/debugging-getting-started",
            "https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick",
            "https://nodejs.org/en/docs/guides/blocking-vs-non-blocking",
            "https://nodejs.org/en/docs/guides/backpressuring-in-streams",
            "https://nodejs.org/en/docs/guides/anatomy-of-an-http-transaction",
            "https://nodejs.org/en/docs/guides/working-with-streams",
            "https://nodejs.org/en/docs/guides/working-with-different-filesystems",
        ]
    },
}


def fetch_url(url, retries=3):
    """Fetch a URL with retries and return text content."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; KeliDocBot/1.0; +https://keli.dev)',
        'Accept': 'text/html,application/xhtml+xml',
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                html_content = resp.read().decode('utf-8', errors='replace')
                return html_content
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"    Failed after {retries} retries: {e}")
                return None


def extract_text_from_html(html_content, source_name):
    """Extract clean text from HTML docs."""
    if not html_content:
        return []

    text = html_content

    # Remove unwanted elements
    for tag in ['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']:
        text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Try to find article/main/content div
    for pattern in [
        r'<article[^>]*>(.*?)</article>',
        r'<main[^>]*>(.*?)</main>',
        r'<div[^>]*class=["\'](?:[^"\']*)(?:content|documentation|prose|post|entry|body)(?:[^"\']*)["\'][^>]*>(.*?)</div>',
        r'<div[^>]*id=["\'](?:[^"\']*)(?:content|documentation|prose|post|main|body)(?:[^"\']*)["\'][^>]*>(.*?)</div>',
        r'<body[^>]*>(.*?)</body>',
    ]:
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1)
            break

    # Remove remaining tags
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)

    # Clean whitespace
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'\s+', ' ', text)

    # Split on headings and double newlines
    chunks = []
    for section in re.split(r'(?=<h[1-6])|\n\s*\n', text):
        section = section.strip()
        if len(section) > 80:
            # Further split long sections by sentences
            sentences = re.split(r'(?<=[.!?])\s+', section)
            current = ''
            for s in sentences:
                if len(current) + len(s) < 500:
                    current += ' ' + s if current else s
                else:
                    if len(current) > 80:
                        chunks.append(current.strip())
                    current = s
            if len(current) > 80:
                chunks.append(current.strip())
    return chunks


def scrape_source(source_name, pages):
    """Scrape all pages for a source and extract text chunks."""
    print(f"\nScraping {source_name} ({len(pages)} pages)...")
    all_chunks = []
    for i, url in enumerate(pages):
        print(f"  [{i+1}/{len(pages)}] {url.split('/')[-1][:40]}...", end=' ', flush=True)
        html_content = fetch_url(url)
        if html_content:
            chunks = extract_text_from_html(html_content, source_name)
            all_chunks.extend(chunks)
            print(f"{len(chunks)} chunks")
        else:
            print("FAILED")
        time.sleep(1)
    return all_chunks


def chunks_to_examples(chunks, source_name, domain, mode='plan'):
    """Convert text chunks to training examples."""
    examples = []
    for chunk in chunks:
        if len(chunk) < 50:
            continue
        # Split into prompt and target
        sentences = re.split(r'(?<=[.!?])\s+', chunk)
        if len(sentences) < 2:
            continue

        # Take first sentence as prompt, rest as target
        prompt = sentences[0]
        target = ' '.join(sentences[1:])

        # Cap lengths
        prompt_tokens = t(prompt)[:128]
        target_tokens = t(target)[:384]

        if len(prompt_tokens) < 3 or len(target_tokens) < 5:
            continue

        input_ids = [BOS] + prompt_tokens + [14]
        target_ids = [4] + target_tokens + [EOS]

        h = hashlib.md5(chunk.encode()).hexdigest()[:16]
        examples.append({
            'input_ids': input_ids[:256],
            'target_ids': target_ids[:512],
            'mode': mode,
            'domain': domain,
            'source': source_name,
            'id': h,
        })
    return examples


def generate_code_examples(existing_chunks, source_name, domain):
    """Generate code-focused examples from documentation text."""
    examples = []
    code_patterns = [
        r'```(\w+)?\n(.*?)```',
        r'<code>(.*?)</code>',
        r'const\s+\w+\s*=\s*[^;]+;',
        r'function\s+\w+\s*\([^)]*\)\s*\{',
        r'class\s+\w+[\s\S]*?(?:\{|:)',
        r'import\s+.*?from\s+[\'"].*?[\'"]',
        r'def\s+\w+\s*\([^)]*\)\s*:',
        r'@app\.(?:get|post|put|delete|route)\(',
    ]

    for chunk in existing_chunks:
        for pattern in code_patterns:
            matches = re.findall(pattern, chunk, re.DOTALL)
            for m in matches:
                if isinstance(m, tuple):
                    code = m[1].strip()
                else:
                    code = m.strip()
                if len(code) < 10 or len(code) > 2000:
                    continue
                code_tokens = t(code)[:512]
                if len(code_tokens) < 5:
                    continue

                prompt = f"Write code for {domain} task using {source_name}"
                prompt_tokens = t(prompt)[:64]

                input_ids = [BOS] + prompt_tokens + [14]
                target_ids = [5] + code_tokens + [EOS]

                h = hashlib.md5(code.encode()).hexdigest()[:16]
                examples.append({
                    'input_ids': input_ids[:256],
                    'target_ids': target_ids[:512],
                    'mode': 'build',
                    'domain': domain,
                    'source': source_name,
                    'id': h,
                })
    return examples


def deduplicate(examples):
    """Remove duplicates by id."""
    seen = set()
    deduped = []
    for ex in examples:
        if ex['id'] not in seen:
            seen.add(ex['id'])
            deduped.append(ex)
    return deduped


def main():
    print("="*60)
    print("GOLD-STANDARD DOCUMENTATION SCRAPER")
    print("="*60)
    print("Sources:", list(SOURCES.keys()))

    all_examples = []
    domain_map = {
        'python': 'backend',
        'react': 'frontend',
        'mdn_html': 'frontend',
        'mdn_css': 'design',
        'mdn_js': 'frontend',
        'fastapi': 'backend',
        'flask': 'backend',
        'sqlite': 'backend',
        'git': 'backend',
        'design': 'design',
        'nodejs': 'backend',
    }

    for source_name, source_info in SOURCES.items():
        domain = domain_map.get(source_name, 'backend')
        chunks = scrape_source(source_name, source_info['pages'])
        print(f"  Total chunks: {len(chunks)}")

        doc_examples = chunks_to_examples(chunks, source_name, domain, mode='plan')
        code_examples = generate_code_examples(chunks, source_name, domain)
        examples = doc_examples + code_examples
        all_examples.extend(examples)

        print(f"  Generated: {len(examples)} training examples")

        # Save per-source
        with open(f'{OUT_DIR}/{source_name}.jsonl', 'w') as f:
            for ex in examples:
                f.write(json.dumps(ex) + '\n')
        print(f"  Saved to {OUT_DIR}/{source_name}.jsonl")

    all_examples = deduplicate(all_examples)
    random.shuffle(all_examples)

    split = int(len(all_examples) * 0.9)
    train = all_examples[:split]
    val = all_examples[split:]

    with open(f'{OUT_DIR}/train.jsonl', 'w') as f:
        for ex in train:
            f.write(json.dumps(ex) + '\n')
    with open(f'{OUT_DIR}/val.jsonl', 'w') as f:
        for ex in val:
            f.write(json.dumps(ex) + '\n')

    domain_counts = {}
    for ex in all_examples:
        d = ex.get('domain', 'unknown')
        domain_counts[d] = domain_counts.get(d, 0) + 1

    print(f"\n{'='*60}")
    print(f"TOTAL: {len(all_examples)} examples")
    print(f"  Train: {len(train)} | Val: {len(val)}")
    print(f"  Domain breakdown: {json.dumps(domain_counts, indent=2)}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
