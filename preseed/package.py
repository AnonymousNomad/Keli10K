import json
import numpy as np
import time
from pathlib import Path

DOCS = {
    'python': [
        {'url': 'docs.python.org/3/tutorial/introduction.html', 'title': 'Python Introduction', 'snippet': 'Python is an easy to learn, powerful programming language. It has efficient high-level data structures and a simple but effective approach to object-oriented programming.'},
        {'url': 'docs.python.org/3/tutorial/controlflow.html', 'title': 'Control Flow', 'snippet': 'The if statement is used for conditional execution. The for statement iterates over items of a sequence. The while statement executes as long as a condition is true.'},
        {'url': 'docs.python.org/3/tutorial/datastructures.html', 'title': 'Data Structures', 'snippet': 'Lists are mutable sequences, typically used to store collections of homogeneous items. Tuples are immutable sequences. Dictionaries store key-value pairs.'},
        {'url': 'docs.python.org/3/library/functions.html', 'title': 'Built-in Functions', 'snippet': 'print() writes to stdout. len() returns length. range() generates arithmetic progressions. map() applies a function to every item. filter() selects items where function is true.'},
        {'url': 'docs.python.org/3/tutorial/modules.html', 'title': 'Modules', 'snippet': 'A module is a file containing Python definitions and statements. The import statement allows using definitions from a module.'},
    ],
    'react': [
        {'url': 'react.dev/learn/describing-the-ui', 'title': 'Describing the UI', 'snippet': 'React components are JavaScript functions that return markup. JSX is a syntax extension that lets you write HTML-like markup inside a JavaScript file.'},
        {'url': 'react.dev/learn/adding-interactivity', 'title': 'Adding Interactivity', 'snippet': 'useState is a React Hook that lets you add a state variable to your component. State is local and isolated between components.'},
        {'url': 'react.dev/learn/managing-state', 'title': 'Managing State', 'snippet': 'useReducer is for complex state logic. Context lets a component receive information from distant parents without passing it as props.'},
        {'url': 'react.dev/learn/escape-hatches', 'title': 'Escape Hatches', 'snippet': 'useRef lets you hold a value that is not used for rendering. useEffect lets you synchronize a component with an external system.'},
        {'url': 'react.dev/reference/react/hooks', 'title': 'Hooks Reference', 'snippet': 'Hooks let you use state and other React features without writing a class. Built-in hooks include useState, useEffect, useContext, useRef, useMemo.'},
    ],
    'css': [
        {'url': 'developer.mozilla.org/en-US/docs/Web/CSS', 'title': 'CSS Reference', 'snippet': 'Cascading Style Sheets is a stylesheet language used to describe the presentation of a document written in HTML. CSS describes how elements should be rendered.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout', 'title': 'CSS Grid', 'snippet': 'CSS Grid Layout is a two-dimensional layout system for the web. It lets you lay out items in columns and rows. The grid container is defined with display: grid.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout', 'title': 'Flexbox', 'snippet': 'Flexbox is a one-dimensional layout method for arranging items in rows or columns. Items flex to fill additional space and shrink to fit into smaller spaces.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations', 'title': 'CSS Animations', 'snippet': 'CSS animations make it possible to animate transitions from one CSS style configuration to another. Animations consist of keyframes.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/CSS/CSS_Box_Model', 'title': 'Box Model', 'snippet': 'The CSS box model describes the rectangular boxes that are generated for elements. Each box has content area, padding, border, and margin.'},
    ],
    'javascript': [
        {'url': 'developer.mozilla.org/en-US/docs/Web/JavaScript/Guide', 'title': 'JS Guide', 'snippet': 'JavaScript is a cross-platform, object-oriented scripting language. It is a small and lightweight language. Inside a host environment, JavaScript can connect to objects of its environment.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise', 'title': 'Promise', 'snippet': 'The Promise object represents the eventual completion or failure of an asynchronous operation. A Promise is in one of these states: pending, fulfilled, rejected.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/API/Fetch_API', 'title': 'Fetch API', 'snippet': 'The Fetch API provides an interface for fetching resources. fetch() returns a Promise that resolves to the Response object representing the response to the request.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array', 'title': 'Array Methods', 'snippet': 'Arrays are list-like objects. map() creates a new array with results of calling a function. filter() creates a new array with elements that pass a test.'},
        {'url': 'developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON', 'title': 'JSON', 'snippet': 'JSON.parse() parses a JSON string. JSON.stringify() converts a JavaScript value to a JSON string.'},
    ],
}


class PreseedPacker:
    def __init__(self, embed_dim=128):
        self.embed_dim = embed_dim
        self.rng = np.random.RandomState(42)

    def _make_embedding(self, text):
        h = abs(hash(text)) % (2**31)
        self.rng = np.random.RandomState(h)
        emb = self.rng.randn(self.embed_dim).astype(np.float32)
        emb = emb / (np.linalg.norm(emb) + 1e-8)
        return emb.tolist()

    def pack(self, output_dir='preseed'):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        all_docs = []

        for domain, entries in DOCS.items():
            domain_docs = []
            for entry in entries:
                doc = {
                    'url': entry['url'],
                    'title': entry['title'],
                    'domain': domain,
                    'snippet': entry['snippet'],
                    'embedding': self._make_embedding(entry['title'] + ' ' + entry['snippet']),
                }
                domain_docs.append(doc)
            all_docs.extend(domain_docs)

            domain_path = output_dir / f'{domain}.json'
            with open(domain_path, 'w') as f:
                json.dump(domain_docs, f, indent=2)
            print(f"  Packed {len(domain_docs)} docs to {domain_path}")

        manifest = {
            'domains': list(DOCS.keys()),
            'total_docs': len(all_docs),
            'embed_dim': self.embed_dim,
            'version': '1.0.0',
        }
        with open(output_dir / 'manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"Preseed manifest: {manifest['total_docs']} total docs across {len(manifest['domains'])} domains")
        return all_docs

    def load_into_hippocampus(self, hippocampus, pack_dir='preseed'):
        pack_dir = Path(pack_dir)
        manifest_path = pack_dir / 'manifest.json'
        if not manifest_path.exists():
            print(f"No manifest found at {manifest_path}")
            return 0

        with open(manifest_path) as f:
            manifest = json.load(f)

        count = 0
        for domain in manifest['domains']:
            domain_path = pack_dir / f'{domain}.json'
            if not domain_path.exists():
                continue
            with open(domain_path) as f:
                docs = json.load(f)
            for doc in docs:
                hippocampus.add_episode(
                    query_embed=np.array(doc['embedding'], dtype=np.float32),
                    snippets=[doc['snippet']],
                    bot_ids=[hash(doc['domain']) % 1000],
                    timestamp=time.time()
                )
                count += 1
        print(f"Loaded {count} preseed docs into hippocampus")
        return count


if __name__ == '__main__':
    packer = PreseedPacker()
    docs = packer.pack()
    print(f"Preseed package ready: {len(docs)} docs")
