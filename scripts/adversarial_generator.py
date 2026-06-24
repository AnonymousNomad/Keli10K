import sys
import os
import random
import json

sys.path.insert(0, '.')
from snca_tokenizer import SNCATokenizer

BOS = 2
EOS = 1
PAD = 0
PLAN = 4
EXECUTION = 5
REFLECTION = 6
UNSURE = 10

SEED = 42
MAX_TOTAL_TOKENS = 1024
SECTION1_COUNT = 8000
SECTION2_COUNT = 4000
SECTION3_COUNT = 3000


def encode(tokenizer, text):
    return tokenizer.encode(str(text), bos=False, eos=False)


def truncate_pair(input_ids, target_ids, max_total=MAX_TOTAL_TOKENS):
    if len(input_ids) + len(target_ids) > max_total:
        if len(target_ids) > max_total // 2:
            target_ids = target_ids[:max_total // 2]
        if len(input_ids) + len(target_ids) > max_total:
            input_ids = input_ids[:max_total - len(target_ids)]
    return input_ids, target_ids


def make_record(input_ids, target_ids, domain, adversarial):
    input_ids, target_ids = truncate_pair(input_ids, target_ids)
    return {
        "input_ids": input_ids,
        "target_ids": target_ids,
        "mode": "plan",
        "domain": domain,
        "adversarial": adversarial,
    }


def encode_with_prompt(tokenizer, prompt, code):
    full = prompt + code
    return encode(tokenizer, full)


def encode_target(tokenizer, reflection, excode):
    full = f"<REFLECTION>{reflection}</REFLECTION><EXECUTION>{excode}</EXECUTION>"
    return encode(tokenizer, full)


# ============================================================
# SECTION 1: POISONED CODE EXAMPLES
# ============================================================

INPUT_PROMPTS = [
    "Fix this code:\n",
    "Review this code:\n",
    "What's wrong here?\n",
    "Find the bug:\n",
    "Can you spot the issue?\n",
    "This code is broken. Fix it:\n",
    "Identify the flaw:\n",
    "Debug this:\n",
]

FLAW_INTROS = [
    "This code has {flaw}. ",
    "The problem is {flaw}. ",
    "There's a critical flaw: {flaw}. ",
    "The issue here is {flaw}. ",
]

DANGER_PHRASES = [
    "Here's why it's dangerous: {danger}",
    "This can cause: {danger}",
    "The risks include: {danger}",
    "This leads to: {danger}",
    "Impact: {danger}",
]


def make_poisoned(tokenizer, prompt_idx, code, flaw, danger, fix_code):
    p = INPUT_PROMPTS[prompt_idx % len(INPUT_PROMPTS)]
    fi = FLAW_INTROS[random.randint(0, len(FLAW_INTROS) - 1)].format(flaw=flaw)
    d = DANGER_PHRASES[random.randint(0, len(DANGER_PHRASES) - 1)].format(danger=danger)
    reflection = fi + d
    input_ids = encode_with_prompt(tokenizer, p, code)
    target_ids = encode_target(tokenizer, reflection, fix_code)
    return make_record(input_ids, target_ids, "adversarial", True)


# ---- Category templates ----

BROKEN_HTML = [
    {
        "code": "<div><p>Some text</div>",
        "flaw": "a missing closing </p> tag",
        "danger": "unclosed tags break DOM structure causing layout failures across browsers",
        "fix": "<div><p>Some text</p></div>"
    },
    {
        "code": """<div class=invalid>content</div>""",
        "flaw": "an unquoted attribute value in class=invalid",
        "danger": "attribute parsing breaks entirely, allowing attribute injection attacks",
        "fix": """<div class="invalid">content</div>"""
    },
    {
        "code": "<img src=>",
        "flaw": "an empty src attribute on the img tag",
        "danger": "the browser sends a request to the current page URL, causing performance and CSRF issues",
        "fix": "<img src=\"placeholder.png\" alt=\"description\">"
    },
    {
        "code": "<!DOCTYPE html><html><head><title>Page",
        "flaw": "missing closing </title></head><body> tags",
        "danger": "the browser enters quirks mode, rendering content unpredictably",
        "fix": "<!DOCTYPE html><html><head><title>Page</title></head><body></body></html>"
    },
    {
        "code": "<a href=\"javascript:void(0)\">click</a>",
        "flaw": "a javascript: URI in the href attribute",
        "danger": "breaks accessibility, right-click workflows, and is a vector for XSS",
        "fix": "<a href=\"#\" onclick=\"return false;\">click</a>"
    },
    {
        "code": "<table><tr><td>cell</table>",
        "flaw": "a missing closing </td> and </tr> tag",
        "danger": "browsers auto-close but render the table incorrectly across different user agents",
        "fix": "<table><tr><td>cell</td></tr></table>"
    },
    {
        "code": "<form><input type=text name=user><button>Submit</form>",
        "flaw": "unquoted attribute values on input and missing </button>",
        "danger": "form state breaks; unquoted attributes allow injection",
        "fix": "<form><input type=\"text\" name=\"user\"><button>Submit</button></form>"
    },
    {
        "code": """<div style="color: red">text<div>""",
        "flaw": "a missing closing </div> tag at the end",
        "danger": "nested divs cascade errors, breaking the entire page layout below this point",
        "fix": """<div style="color: red">text</div>"""
    },
    {
        "code": "<html><body><h1>Title<hr><p>text",
        "flaw": "missing closing </h1> and </body></html> tags",
        "danger": "HTML validation fails and browser compatibility degrades significantly",
        "fix": "<html><body><h1>Title</h1><hr><p>text</p></body></html>"
    },
    {
        "code": "<div id=1 class=foo>content</div>",
        "flaw": "a numeric id value starting with a digit",
        "danger": "CSS selectors like #1 are invalid; DOM queries with getElementById fail",
        "fix": "<div id=\"id1\" class=\"foo\">content</div>"
    },
    {
        "code": "<script>alert('hello')<script>",
        "flaw": "a missing closing </script> tag (inner <script> is not a valid close)",
        "danger": "the entire rest of the page becomes part of the script, breaking all JS",
        "fix": "<script>alert('hello')</script>"
    },
    {
        "code": "<option value=>Choose</option>",
        "flaw": "an empty value attribute on option",
        "danger": "form submissions send unexpected values; breaks server-side validation",
        "fix": "<option value=\"\">Choose</option>"
    },
    {
        "code": """<div class="container"<p>text</p></div>""",
        "flaw": "a missing > after the class attribute closing quote",
        "danger": "the parser fails catastrophically and may expose raw HTML",
        "fix": """<div class="container"><p>text</p></div>"""
    },
    {
        "code": "<meta charset=utf-8>",
        "flaw": "a missing closing / in the self-closing meta tag",
        "danger": "some HTML parsers treat this as the start of a normal element causing layout issues",
        "fix": "<meta charset=\"utf-8\">"
    },
    {
        "code": "<ul><li>Item 1<li>Item 2</ul>",
        "flaw": "missing closing </li> tags for each list item",
        "danger": "nested lists and screen readers fail to interpret structure correctly",
        "fix": "<ul><li>Item 1</li><li>Item 2</li></ul>"
    },
    {
        "code": "<button onclick='return confirm('sure?')'>Delete</button>",
        "flaw": "nested single quotes in the onclick handler",
        "danger": "the event handler string breaks at the inner quote, executing malformed JS",
        "fix": """<button onclick="return confirm('sure?')">Delete</button>"""
    },
    {
        "code": "<iframe src=\"https://example.com\">",
        "flaw": "missing closing </iframe> tag",
        "danger": "the browser embeds everything after as iframe content, breaking page structure",
        "fix": "<iframe src=\"https://example.com\"></iframe>"
    },
    {
        "code": "<style>body { color: red }</style><body><p>text",
        "flaw": "a style element placed in the body instead of head",
        "danger": "some browsers require styles in head; FOUC and invalid HTML result",
        "fix": "<!DOCTYPE html><html><head><style>body { color: red }</style></head><body><p>text</p></body></html>"
    },
    {
        "code": "<a href='https://site.com' onclick='navigate()'>link</a>",
        "flaw": "missing rel=\"noopener\" on a target=_blank link",
        "danger": "the opened page can access window.opener and redirect the original tab (tabnabbing)",
        "fix": "<a href='https://site.com' target='_blank' rel='noopener noreferrer'>link</a>"
    },
    {
        "code": "<form action='/submit'><input name='x'><button>Go</form>",
        "flaw": "missing method attribute defaulting to GET on a form with side effects",
        "danger": "sensitive data is appended to the URL and logged by proxies",
        "fix": "<form action='/submit' method='POST'><input name='x'><button>Go</button></form>"
    },
    {
        "code": "<html xmlns=\"http://www.w3.org/1999/xhtml\"><body>text",
        "flaw": "XHTML namespace on a text/html document",
        "danger": "the browser may enforce strict parsing rules causing render differences",
        "fix": "<!DOCTYPE html><html><body>text</body></html>"
    },
    {
        "code": """<div onclick="alert('click')" style="cursor:pointer">Click</div>""",
        "flaw": "inline event handler mixed with inline style",
        "danger": "violates CSP policies and prevents separation of concerns; maintainability suffers",
        "fix": """<div id="clickable">Click</div><script>document.getElementById('clickable').onclick = () => alert('click');</script>"""
    },
    {
        "code": "<nav><a href='/'>Home<a href='/about'>About</nav>",
        "flaw": "missing closing </a> tag before the second anchor",
        "danger": "the second anchor becomes nested inside the first, breaking navigation",
        "fix": "<nav><a href='/'>Home</a><a href='/about'>About</a></nav>"
    },
]

BROKEN_CSS = [
    {
        "code": ".box { width: 100; height: 50; }",
        "flaw": "missing units on width and height values",
        "danger": "the browser ignores invalid values and the element collapses to 0px",
        "fix": ".box { width: 100px; height: 50px; }"
    },
    {
        "code": ".box { margin: red; }",
        "flaw": "a color value used where a length is expected for margin",
        "danger": "the entire margin declaration is ignored; layout breaks silently",
        "fix": ".box { margin: 10px; }"
    },
    {
        "code": "@media screen { body { color: blue }",
        "flaw": "missing closing brace for the @media block",
        "danger": "all CSS after this point is consumed as part of the @media rule and breaks",
        "fix": "@media screen { body { color: blue; } }"
    },
    {
        "code": ".class { color: red; font-size: 12 }",
        "flaw": "missing px unit on font-size",
        "danger": "font-size: 12 is treated as invalid; falls back to browser default",
        "fix": ".class { color: red; font-size: 12px; }"
    },
    {
        "code": "div { background: url(image.jpg) }",
        "flaw": "missing quotes or escaped paths in url()",
        "danger": "URLs with spaces or special chars break; no background loads",
        "fix": "div { background: url('image.jpg'); }"
    },
    {
        "code": "* { box-sizing: border-box }",
        "flaw": "missing semicolon at the end of the declaration",
        "danger": "if another rule follows, the parser skips both declarations",
        "fix": "* { box-sizing: border-box; }"
    },
    {
        "code": ".container { display: flex; gap: 20; }",
        "flaw": "missing unit on the gap property",
        "danger": "gap: 20 is invalid; Flexbox gap defaults to 0",
        "fix": ".container { display: flex; gap: 20px; }"
    },
    {
        "code": "h1 { color: blue; color: red !important; color: green }",
        "flaw": "multiple conflicting color declarations with specificities",
        "danger": "maintainers cannot predict which rule wins; debugging is extremely hard",
        "fix": "h1 { color: red !important; }"
    },
    {
        "code": ".nav { position: fixed; top: 0; left: 0; width: 100% }",
        "flaw": "missing z-index on a fixed-position element",
        "danger": "the nav appears behind other positioned elements; critical UI is hidden",
        "fix": ".nav { position: fixed; top: 0; left: 0; width: 100%; z-index: 1000; }"
    },
    {
        "code": "@import url('style.css'); @import url('reset.css');",
        "flaw": "@import rules placed after other CSS rules or in the body",
        "danger": "@import must be at the top of the stylesheet; otherwise it's ignored",
        "fix": "@import url('reset.css'); @import url('style.css');"
    },
    {
        "code": ".grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr; }",
        "flaw": "repeating identical column definitions without repeat()",
        "danger": "unnecessary repetition makes code hard to maintain and change",
        "fix": ".grid { display: grid; grid-template-columns: repeat(5, 1fr); }"
    },
    {
        "code": "a { text-decoration: none; color: blue; } a:visited { color: purple; }",
        "flaw": "no focus-visible or outline styles for keyboard navigation",
        "danger": "keyboard users cannot see which element is focused; accessibility violation",
        "fix": "a { text-decoration: none; color: blue; } a:focus-visible { outline: 2px solid blue; }"
    },
    {
        "code": ".modal { position: absolute; }",
        "flaw": "using absolute instead of fixed for a modal overlay",
        "danger": "the modal scrolls with the page instead of staying centered; broken UX",
        "fix": ".modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); }"
    },
    {
        "code": "p { font-weight: bold; font-style: italic; }",
        "flaw": "no font-family fallback for system fonts",
        "danger": "on systems without the specified font, text renders in default serif",
        "fix": "p { font-weight: bold; font-style: italic; font-family: 'Helvetica', Arial, sans-serif; }"
    },
    {
        "code": "body { overflow: hidden; }",
        "flaw": "overflow:hidden on the body element globally",
        "danger": "content that overflows is silently clipped; users can never scroll",
        "fix": "body { overflow-x: hidden; overflow-y: auto; }"
    },
    {
        "code": "div { transition: all 0.3s; }",
        "flaw": "using 'all' in transition property",
        "danger": "performance suffers as every property change triggers a repaint",
        "fix": "div { transition: opacity 0.3s, transform 0.3s; }"
    },
    {
        "code": ".row::before { content: ''; display: table; } .row::after { content: ''; display: table; }",
        "flaw": "using ::before and ::after on the same element for clearfix",
        "danger": "only one ::before and one ::after pseudo-element exist per element; duplicates are ignored",
        "fix": ".row::after { content: ''; display: table; clear: both; }"
    },
    {
        "code": "@keyframes slide { from { left: 0; } to { left: 100px; } } .el { animation: slide 1s; }",
        "flaw": "animating left instead of transform for movement",
        "danger": "left triggers layout recalculations causing jank and poor performance",
        "fix": "@keyframes slide { from { transform: translateX(0); } to { transform: translateX(100px); } } .el { animation: slide 1s; }"
    },
    {
        "code": ".btn { background-color: blue; border: none; color: white; padding: 10px 20px; }",
        "flaw": "using a generic color name instead of a design token or variable",
        "danger": "theme changes require finding and replacing every instance site-wide",
        "fix": ".btn { background-color: var(--color-primary); border: none; color: var(--color-on-primary); padding: 10px 20px; }"
    },
    {
        "code": "img { width: 100%; height: auto; }",
        "flaw": "missing max-width: 100% on responsive images",
        "danger": "images larger than their container overflow and break layout",
        "fix": "img { max-width: 100%; height: auto; display: block; }"
    },
    {
        "code": "p { line-height: 1; }",
        "flaw": "unitless line-height of 1 on body text",
        "danger": "text lines collide and become unreadable for multi-line paragraphs",
        "fix": "p { line-height: 1.6; }"
    },
    {
        "code": ".card { box-shadow: 0 2px 4px black; }",
        "flaw": "using black instead of rgba for shadows",
        "danger": "shadows appear as solid black blobs instead of semi-transparent overlays",
        "fix": ".card { box-shadow: 0 2px 4px rgba(0,0,0,0.15); }"
    },
    {
        "code": "div { width: 100%; padding: 20px; }",
        "flaw": "box-sizing not set, so padding increases element width beyond 100%",
        "danger": "the element overflows its parent by 40px, breaking horizontal layout",
        "fix": "div { box-sizing: border-box; width: 100%; padding: 20px; }"
    },
]

BROKEN_JS = [
    {
        "code": "function add(a, b) { return a + b; } console.log(suma(1, 2));",
        "flaw": "a ReferenceError: suma is not defined (typo in function name)",
        "danger": "the script crashes at runtime with no early warning; no type checking catches it",
        "fix": "function add(a, b) { return a + b; } console.log(add(1, 2));"
    },
    {
        "code": "async function load() { const data = fetch('/api/data'); console.log(data.json()); }",
        "flaw": "missing await before fetch() and before data.json()",
        "danger": "the function returns a Promise object, not the actual data; json() call fails",
        "fix": "async function load() { const res = await fetch('/api/data'); const data = await res.json(); console.log(data); }"
    },
    {
        "code": "for (var i = 0; i < 5; i++) { setTimeout(function() { console.log(i); }, 100); }",
        "flaw": "var instead of let creates a closure over the same i variable",
        "danger": "every callback prints 5 instead of 0-4; classic closure leak bug",
        "fix": "for (let i = 0; i < 5; i++) { setTimeout(function() { console.log(i); }, 100); }"
    },
    {
        "code": "if (x = 5) { console.log('x is 5'); }",
        "flaw": "assignment = instead of comparison ===",
        "danger": "the condition always evaluates to truthy (5 is truthy); introduces silent logic bug",
        "fix": "if (x === 5) { console.log('x is 5'); }"
    },
    {
        "code": "const obj = { name: 'test' }; console.log(obj.nmae);",
        "flaw": "a property access typo (nmae instead of name)",
        "danger": "returns undefined silently instead of throwing, making debugging extremely difficult",
        "fix": "const obj = { name: 'test' }; console.log(obj.name);"
    },
    {
        "code": "const arr = [1, 2, 3]; console.log(arr.includes('2'));",
        "flaw": "type mismatch: includes() uses strict equality; string '2' !== number 2",
        "danger": "returns false when the value is actually present in the array",
        "fix": "const arr = [1, 2, 3]; console.log(arr.includes(2));"
    },
    {
        "code": "function process(items) { items.forEach(item => { item.value = item.value * 2; }); return items; }",
        "flaw": "mutating the original array instead of creating a new one with .map()",
        "danger": "side effects modify caller's data; causes unpredictable state changes",
        "fix": "function process(items) { return items.map(item => ({ ...item, value: item.value * 2 })); }"
    },
    {
        "code": "const data = JSON.parse(userInput);",
        "flaw": "unvalidated JSON.parse() on untrusted user input",
        "danger": "malformed JSON throws; prototype pollution via __proto__ is possible",
        "fix": "let data; try { data = JSON.parse(userInput); } catch { data = null; }"
    },
    {
        "code": "const result = '5' + 3 - 1; console.log(result);",
        "flaw": "unexpected type coercion: '5' + 3 is '53', then '53' - 1 is 52",
        "danger": "string concatenation and numeric subtraction produce counterintuitive results",
        "fix": "const result = Number('5') + 3 - 1; console.log(result);"
    },
    {
        "code": "function save() { value = 10; }",
        "flaw": "assignment to an undeclared variable creates a global",
        "danger": "pollutes the global namespace; causes hard-to-find collisions",
        "fix": "function save() { let value = 10; }"
    },
    {
        "code": "const promise = new Promise((resolve, reject) => { doSomething(); resolve(); });",
        "flaw": "no error handling inside the Promise executor",
        "danger": "if doSomething() throws, the promise hangs forever (unhandled rejection)",
        "fix": "const promise = new Promise((resolve, reject) => { try { doSomething(); resolve(); } catch (e) { reject(e); } });"
    },
    {
        "code": "const user = getUser(); console.log(user.name.toUpperCase());",
        "flaw": "no null check before accessing .name or calling .toUpperCase()",
        "danger": "if user or user.name is null/undefined, the script throws a TypeError and crashes",
        "fix": "const user = getUser(); console.log(user?.name?.toUpperCase() ?? '');"
    },
    {
        "code": "let a = 1; let b = 2; let c = a + b; console.log('Result: ' + c); // comment this",
        "flaw": "the comment // comment this is on the same line but doesn't comment anything",
        "danger": "misleading; the line still executes and c is computed",
        "fix": "let a = 1; let b = 2; let c = a + b; console.log('Result: ' + c);"
    },
    {
        "code": "const arr = [1, 2, 3]; delete arr[1]; console.log(arr.length);",
        "flaw": "delete on an array element leaves a hole (empty slot)",
        "danger": "arr.length stays 3 but arr[1] is undefined; causes sparse array bugs",
        "fix": "const arr = [1, 2, 3]; arr.splice(1, 1); console.log(arr.length);"
    },
    {
        "code": "console.log(0.1 + 0.2 === 0.3);",
        "flaw": "floating point arithmetic precision issue",
        "danger": "0.1 + 0.2 = 0.30000000000000004, so the comparison returns false",
        "fix": "console.log(Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON);"
    },
    {
        "code": "const x = [1, 2, 3]; const y = x; y.push(4); console.log(x.length);",
        "flaw": "y is a reference, not a copy; mutating y also mutates x",
        "danger": "unexpected aliasing causes data corruption across the codebase",
        "fix": "const x = [1, 2, 3]; const y = [...x]; y.push(4); console.log(x.length);"
    },
    {
        "code": "function check() { if (true) { var x = 5; } console.log(x); }",
        "flaw": "var is function-scoped, not block-scoped; x leaks out of the if block",
        "danger": "variables are accessible outside their intended scope, causing name collisions",
        "fix": "function check() { if (true) { let x = 5; console.log(x); } }"
    },
    {
        "code": "setTimeout(doSomething(), 1000);",
        "flaw": "calling doSomething() immediately instead of passing the function reference",
        "danger": "the function runs instantly, not after 1 second; the timeout does nothing",
        "fix": "setTimeout(doSomething, 1000);"
    },
    {
        "code": "const el = document.getElementById('btn'); el.addEventListener('click', handleClick);",
        "flaw": "no null check before calling addEventListener on getElementById result",
        "danger": "if #btn doesn't exist, the script throws and all subsequent JS stops",
        "fix": "const el = document.getElementById('btn'); el?.addEventListener('click', handleClick);"
    },
    {
        "code": "for (const key in obj) { console.log(obj[key]); }",
        "flaw": "for...in iterates inherited enumerable properties, not just own keys",
        "danger": "if the prototype has been extended, unexpected keys appear in iteration",
        "fix": "for (const key of Object.keys(obj)) { console.log(obj[key]); }"
    },
    {
        "code": "const r = arr.filter(x => x > 2).map(x => x * 2).filter(x => x > 5).map(x => x - 1);",
        "flaw": "chaining multiple filter().map() instead of using reduce() for a single pass",
        "danger": "O(4n) instead of O(n); performance degrades on large arrays",
        "fix": "const r = arr.reduce((acc, x) => { const doubled = x * 2; if (doubled > 5) acc.push(doubled - 1); return acc; }, []);"
    },
    {
        "code": "const val = someValue || 'default';",
        "flaw": "using || instead of ?? for default values",
        "danger": "|| treats '', 0, false, and null as falsy; all get overwritten with 'default'",
        "fix": "const val = someValue ?? 'default';"
    },
]

BROKEN_REACT = [
    {
        "code": "function List({ items }) { return items.map(item => <li>{item}</li>); }",
        "flaw": "missing key prop on mapped <li> elements",
        "danger": "React cannot identify which items changed; causes re-render bugs and poor performance",
        "fix": "function List({ items }) { return items.map((item, i) => <li key={item.id || i}>{item}</li>); }"
    },
    {
        "code": "function Timer() { const [count, setCount] = useState(0); useEffect(() => { setInterval(() => { setCount(count + 1); }, 1000); }, []); return <div>{count}</div>; }",
        "flaw": "stale closure: setCount(count + 1) captures the initial count (0) forever",
        "danger": "count never increments past 1; the timer appears broken",
        "fix": "function Timer() { const [count, setCount] = useState(0); useEffect(() => { const id = setInterval(() => { setCount(c => c + 1); }, 1000); return () => clearInterval(id); }, []); return <div>{count}</div>; }"
    },
    {
        "code": "function Counter() { const [count, setCount] = useState(0); setCount(count + 1); return <div>{count}</div>; }",
        "flaw": "calling setCount directly in the render body (not in an effect or event handler)",
        "danger": "React re-renders immediately, causing an infinite render loop",
        "fix": "function Counter() { const [count, setCount] = useState(0); useEffect(() => { setCount(count + 1); }, []); return <div>{count}</div>; }"
    },
    {
        "code": "function App() { const [user, setUser] = useState(null); useEffect(() => { fetchUser().then(setUser); }); return <div>{user?.name}</div>; }",
        "flaw": "useEffect missing dependency array, runs on every render",
        "danger": "infinite fetch loop: fetch triggers setUser, which triggers re-render, which triggers fetch again",
        "fix": "function App() { const [user, setUser] = useState(null); useEffect(() => { fetchUser().then(setUser); }, []); return <div>{user?.name}</div>; }"
    },
    {
        "code": "function Form() { const [value, setValue] = useState(''); return <input value={value} />; }",
        "flaw": "controlled input without an onChange handler (read-only value prop)",
        "danger": "the user cannot type in the input; the field appears frozen",
        "fix": "function Form() { const [value, setValue] = useState(''); return <input value={value} onChange={e => setValue(e.target.value)} />; }"
    },
    {
        "code": "function MyComponent() { const [name, setName] = useState(''); const [email, setEmail] = useState(''); if (!name) { useState('guest'); } return <div>{name}</div>; }",
        "flaw": "conditionally calling useState inside an if block",
        "danger": "violates the rules of hooks; React throws because hook call order changes between renders",
        "fix": "function MyComponent() { const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [displayName] = useState('guest'); return <div>{name || displayName}</div>; }"
    },
    {
        "code": "function Parent() { const [data, setData] = useState(null); return <Child data={data} onClick={() => setData('new')} />; } function Child({ data, onClick }) { return <button onClick={() => { onClick(); }}>{data}</button>; }",
        "flaw": "unnecessary wrapper function around onClick in Child",
        "danger": "creates a new function reference on every render; breaks React.memo optimization",
        "fix": "function Child({ data, onClick }) { return <button onClick={onClick}>{data}</button>; }"
    },
    {
        "code": "const MyContext = createContext(); function App() { return <MyContext.Provider value={{ user: 'alice' }}><Child /></MyContext.Provider>; } function Child() { const ctx = useContext(MyContext); ctx.user = 'bob'; return <div>{ctx.user}</div>; }",
        "flaw": "mutating the context value directly instead of using state",
        "danger": "mutations don't trigger re-renders; descendants don't see the new value",
        "fix": "function App() { const [user, setUser] = useState('alice'); return <MyContext.Provider value={{ user, setUser }}><Child /></MyContext.Provider>; }"
    },
    {
        "code": "function Search() { const [query, setQuery] = useState(''); const results = useMemo(() => { return expensiveSearch(query); }); return <div>{results}</div>; }",
        "flaw": "useMemo without a dependency array; it recomputes on every render anyway",
        "danger": "no performance benefit but adds overhead; useMemo is useless",
        "fix": "function Search() { const [query, setQuery] = useState(''); const results = useMemo(() => expensiveSearch(query), [query]); return <div>{results}</div>; }"
    },
    {
        "code": "function Component() { const style = { color: 'red', fontSize: 14 }; return <div style={style}>text</div>; }",
        "flaw": "inline style object created every render (camelCase instead of string)",
        "danger": "fine for small cases but breaks performance if style is large or the component rerenders often",
        "fix": "const style = { color: 'red', fontSize: 14 }; function Component() { return <div style={style}>text</div>; }"
    },
    {
        "code": "function Profile({ user }) { const [editing, setEditing] = useState(false); return editing ? <EditForm user={user} /> : <ViewMode user={user} />; }",
        "flaw": "conditional rendering of different component trees but the state persists in the same position",
        "danger": "when toggling back, React sees a different component type and unmounts/remounts, losing state",
        "fix": "function Profile({ user }) { const [editing, setEditing] = useState(false); return <div>{editing ? <EditForm /> : <ViewMode />}</div>; }"
    },
    {
        "code": "function App() { const [items, setItems] = useState([]); function addItem() { items.push({ id: Date.now() }); setItems(items); } return <button onClick={addItem}>Add</button>; }",
        "flaw": "mutating state directly with .push() instead of creating a new array",
        "danger": "React detects no reference change; the component does not re-render",
        "fix": "function App() { const [items, setItems] = useState([]); function addItem() { setItems(prev => [...prev, { id: Date.now() }]); } return <button onClick={addItem}>Add</button>; }"
    },
    {
        "code": "function List() { const [data, setData] = useState([]); useEffect(() => { fetch('/api').then(r => r.json()).then(setData); }, []); return <div>{data.map(d => <p>{d.name}</p>)}</div>; }",
        "flaw": "no loading state, error state, or cleanup",
        "danger": "if the component unmounts before fetch completes, setData on unmounted component causes memory leak",
        "fix": "function List() { const [data, setData] = useState([]); const [loading, setLoading] = useState(true); useEffect(() => { let active = true; fetch('/api').then(r => r.json()).then(d => { if (active) { setData(d); setLoading(false); } }).catch(() => setLoading(false)); return () => { active = false; }; }, []); if (loading) return <p>Loading...</p>; return <div>{data.map(d => <p key={d.id}>{d.name}</p>)}</div>; }"
    },
    {
        "code": "function Tab() { const [tab, setTab] = useState(0); return <div onClick={() => setTab(tab + 1)}>{tab}</div>; } function App() { const [show, setShow] = useState(true); return <div>{show && <Tab />}</div>; }",
        "flaw": "state is lost when toggling the parent show/hide because the component unmounts",
        "danger": "the Tab component's internal count resets to 0 every time show toggles",
        "fix": "function App() { const [show, setShow] = useState(true); return <div style={{ display: show ? 'block' : 'none' }}><Tab /></div>; }"
    },
    {
        "code": "function Form() { const [form, setForm] = useState({ name: '', email: '' }); function handleChange(e) { form[e.target.name] = e.target.value; setForm(form); } return <input name=\"name\" onChange={handleChange} />; }",
        "flaw": "mutating the form object directly and setting the same reference",
        "danger": "React bails out of re-render when it sees the same object reference",
        "fix": "function Form() { const [form, setForm] = useState({ name: '', email: '' }); function handleChange(e) { setForm(prev => ({ ...prev, [e.target.name]: e.target.value })); } return <input name=\"name\" onChange={handleChange} />; }"
    },
    {
        "code": "function Dropdown({ items }) { const [open, setOpen] = useState(false); return <div><button onClick={() => setOpen(!open)}>Toggle</button>{open && <div>{items.map(i => <p>{i}</p>)}</div>}</div>; }",
        "flaw": "parent component can pass open as a prop but state is internal",
        "danger": "the parent has no way to close the dropdown from outside; accessibility issues with no keyboard handler",
        "fix": "function Dropdown({ items, open, onToggle }) { return <div><button onClick={onToggle} aria-expanded={open}>Toggle</button>{open && <div role=\"menu\">{items.map(i => <p key={i}>{i}</p>)}</div>}</div>; }"
    },
    {
        "code": "function App() { const [state, dispatch] = useReducer(reducer, initialState); useEffect(() => { dispatch({ type: 'INIT' }); }); return <div>{state.value}</div>; }",
        "flaw": "useEffect without dependency array dispatches on every render",
        "danger": "dispatch triggers re-render, which triggers effect, creating an infinite loop",
        "fix": "function App() { const [state, dispatch] = useReducer(reducer, initialState); useEffect(() => { dispatch({ type: 'INIT' }); }, []); return <div>{state.value}</div>; }"
    },
    {
        "code": "function List() { const [items, setItems] = useState([1, 2, 3]); return <div>{items.map(i => <div key={Math.random()}>{i}</div>)}</div>; }",
        "flaw": "using Math.random() as the key prop",
        "danger": "React creates a new DOM node on every render because the key changes; destroys all state",
        "fix": "function List() { const [items, setItems] = useState([1, 2, 3]); return <div>{items.map((i, idx) => <div key={idx}>{i}</div>)}</div>; }"
    },
]

BROKEN_PYTHON = [
    {
        "code": "def add(a, b):\nreturn a + b",
        "flaw": "incorrect indentation: return is not indented under the function body",
        "danger": "IndentationError; the function has no body and the return is at module level",
        "fix": "def add(a, b):\n    return a + b"
    },
    {
        "code": "def process(data):\n    result = transform(data)\n    return result\n\nprint(reslt)",
        "flaw": "a NameError: reslt is not defined (typo in variable name)",
        "danger": "the script crashes with no compile-time check, only at runtime",
        "fix": "def process(data):\n    result = transform(data)\n    return result\n\nprint(result)"
    },
    {
        "code": "def append_to(item, lst=[]):\n    lst.append(item)\n    return lst",
        "flaw": "a mutable default argument (lst=[]); the list is shared across calls",
        "danger": "calling append_to(1) returns [1], then append_to(2) returns [1, 2] unexpectedly",
        "fix": "def append_to(item, lst=None):\n    if lst is None:\n        lst = []\n    lst.append(item)\n    return lst"
    },
    {
        "code": "try:\n    risky_operation()\nexcept:\n    pass",
        "flaw": "a bare except that catches ALL exceptions (including KeyboardInterrupt)",
        "danger": "silently suppresses SystemExit, KeyboardInterrupt, making the program unkillable",
        "fix": "try:\n    risky_operation()\nexcept Exception as e:\n    print(f'Error: {e}')"
    },
    {
        "code": "x = 10\nif x = 10:\n    print('ten')",
        "flaw": "assignment = instead of comparison == in the if condition",
        "danger": "SyntaxError; assignments in conditions are always illegal in Python",
        "fix": "x = 10\nif x == 10:\n    print('ten')"
    },
    {
        "code": "for i in range(5):\nprint(i)",
        "flaw": "incorrect indentation: print is not inside the for loop body",
        "danger": "IndentationError; the for loop has no body",
        "fix": "for i in range(5):\n    print(i)"
    },
    {
        "code": "def get_config():\n    with open('config.json') as f:\n        return json.load(f)",
        "flaw": "missing import json at the top of the file",
        "danger": "NameError: json is not defined at runtime",
        "fix": "import json\n\ndef get_config():\n    with open('config.json') as f:\n        return json.load(f)"
    },
    {
        "code": "items = [1, 2, 3]\nfor i in range(len(items)):\n    del items[i]",
        "flaw": "modifying a list while iterating over it with del",
        "danger": "indices shift after deletion; items are skipped and some are never deleted; IndexError possible",
        "fix": "items = [1, 2, 3]\nitems[:] = [x for x in items if condition]"
    },
    {
        "code": "def divide(a, b):\n    return a / b\n\nresult = divide(10, 0)",
        "flaw": "no zero-division check before dividing by b",
        "danger": "ZeroDivisionError crashes the program at runtime",
        "fix": "def divide(a, b):\n    if b == 0:\n        return float('inf')\n    return a / b\n\nresult = divide(10, 0)"
    },
    {
        "code": "class Config:\n    def __init__(self):\n        self.settings = {}\n    def load(self, path):\n        import json\n        with open(path) as f:\n            self.settings = json.load(f)",
        "flaw": "import json inside the method instead of at module level",
        "danger": "relatively harmless but the import is re-executed on every call, wasting cycles",
        "fix": "import json\n\nclass Config:\n    def __init__(self):\n        self.settings = {}\n    def load(self, path):\n        with open(path) as f:\n            self.settings = json.load(f)"
    },
    {
        "code": "def fetch_data(url):\n    import requests\n    response = requests.get(url)\n    return response.text\n\nfetch_data('https://api.example.com')\nprint(data)",
        "flaw": "the return value of fetch_data is not assigned to a variable; data is undefined",
        "danger": "NameError on data; the fetched content is discarded silently",
        "fix": "def fetch_data(url):\n    import requests\n    response = requests.get(url)\n    return response.text\n\ndata = fetch_data('https://api.example.com')\nprint(data)"
    },
    {
        "code": "def cache(func):\n    store = {}\n    def wrapper(*args):\n        if args in store:\n            return store[args]\n        result = func(*args)\n        store[args] = result\n        return result\n    return wrapper\n\n@cache\ndef compute(x):\n    return x * x\n\nprint(compute(5))\nprint(store)",
        "flaw": "accessing store from outside the closure scope",
        "danger": "NameError: store is not accessible globally; implementation detail leak",
        "fix": "def cache(func):\n    store = {}\n    def wrapper(*args):\n        if args in store:\n            return store[args]\n        result = func(*args)\n        store[args] = result\n        return result\n    return wrapper\n\n@cache\ndef compute(x):\n    return x * x\n\nprint(compute(5))"
    },
    {
        "code": "def calculate_total(prices):\n    total = 0\n    for p in prices:\n        total += p\n    return total\n\nprices = [10, 20, '30']\nprint(calculate_total(prices))",
        "flaw": "a list containing a string instead of a number for '30'",
        "danger": "TypeError: unsupported operand type(s) for +=: 'int' and 'str' at runtime",
        "fix": "def calculate_total(prices):\n    total = 0\n    for p in prices:\n        total += float(p)\n    return total\n\nprices = [10, 20, '30']\nprint(calculate_total(prices))"
    },
    {
        "code": "f = open('data.txt', 'r')\ncontent = f.read()\nprint(content)",
        "flaw": "file is opened but never closed, and no context manager is used",
        "danger": "file descriptor leak; eventually the process runs out of file handles",
        "fix": "with open('data.txt', 'r') as f:\n    content = f.read()\nprint(content)"
    },
    {
        "code": "import os\n\ndef run_command(cmd):\n    os.system(cmd)\n\nrun_command('ls -la ' + user_input)",
        "flaw": "os.system() with unsanitized user input",
        "danger": "command injection: user_input can contain '; rm -rf /' or similar",
        "fix": "import subprocess\n\ndef run_command(cmd):\n    subprocess.run(cmd.split(), check=True)"
    },
    {
        "code": "def sort_by_second(x):\n    return x[1]\n\ndata = [(1, 'b'), (2, 'a'), (3, 'c')]\ndata.sort(key=sort_by_second())\nprint(data)",
        "flaw": "calling sort_by_second() instead of passing the function reference",
        "danger": "TypeError: sort expected a callable but got the return value of sort_by_second()",
        "fix": "def sort_by_second(x):\n    return x[1]\n\ndata = [(1, 'b'), (2, 'a'), (3, 'c')]\ndata.sort(key=sort_by_second)\nprint(data)"
    },
    {
        "code": "from datetime import datetime\nimport datetime",
        "flaw": "importing both the module and a specific name from it",
        "danger": "the names conflict; one import overwrites the other, causing confusion",
        "fix": "from datetime import datetime"
    },
    {
        "code": "def get_user(user_id):\n    import sqlite3\n    conn = sqlite3.connect('db.sqlite')\n    cur = conn.cursor()\n    cur.execute(f\"SELECT * FROM users WHERE id = {user_id}\")\n    return cur.fetchone()",
        "flaw": "SQL injection via f-string interpolation in the query",
        "danger": "user_id = '1; DROP TABLE users' deletes the users table",
        "fix": "def get_user(user_id):\n    import sqlite3\n    conn = sqlite3.connect('db.sqlite')\n    cur = conn.cursor()\n    cur.execute(\"SELECT * FROM users WHERE id = ?\", (user_id,))\n    return cur.fetchone()"
    },
    {
        "code": "class A:\n    def __init__(self):\n        self.x = 1\n\nclass B(A):\n    def __init__(self):\n        self.x = 2\n\nb = B()\nprint(b.x)\nprint(A.x)",
        "flaw": "accessing A.x as a class attribute instead of an instance attribute",
        "danger": "AttributeError: type object 'A' has no attribute 'x'",
        "fix": "class A:\n    def __init__(self):\n        self.x = 1\n\nclass B(A):\n    def __init__(self):\n        super().__init__()\n        self.x = 2\n\nb = B()\nprint(b.x)"
    },
    {
        "code": "def outer():\n    x = 10\n    def inner():\n        x += 1\n        return x\n    return inner",
        "flaw": "trying to reassign x in the inner function without nonlocal declaration",
        "danger": "UnboundLocalError: local variable 'x' referenced before assignment",
        "fix": "def outer():\n    x = 10\n    def inner():\n        nonlocal x\n        x += 1\n        return x\n    return inner"
    },
    {
        "code": "result = []\nfor i in range(10):\n    result.append(lambda: i)\nprint([f() for f in result])",
        "flaw": "closures capture the variable i, not its value; all lambdas return 9",
        "danger": "late-binding closure bug; output is [9,9,9,...] instead of [0,1,2,...]",
        "fix": "result = []\nfor i in range(10):\n    result.append(lambda i=i: i)\nprint([f() for f in result])"
    },
    {
        "code": "import threading\n\nbalance = 0\ndef deposit(n):\n    global balance\n    for _ in range(n):\n        balance += 1\n\nthreads = [threading.Thread(target=deposit, args=(100000,)) for _ in range(5)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint(balance)",
        "flaw": "race condition: balance += 1 is not thread-safe",
        "danger": "the final balance is almost never 500000 due to lost updates",
        "fix": "import threading\n\nlock = threading.Lock()\nbalance = 0\ndef deposit(n):\n    global balance\n    for _ in range(n):\n        with lock:\n            balance += 1\n\nthreads = [threading.Thread(target=deposit, args=(100000,)) for _ in range(5)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint(balance)"
    },
    {
        "code": "logged = False\ndef login():\n    global logged\n    logged = True\n    return logged\n\nif login():\n    print('Access granted')\nif login:\n    print('Always runs')",
        "flaw": "referencing the function login instead of calling login() in the second if",
        "danger": "functions are truthy, so the second block always executes regardless of the login state",
        "fix": "logged = False\ndef login():\n    global logged\n    logged = True\n    return logged\n\nif login():\n    print('Access granted')\nif login():\n    print('Also checks')"
    },
    {
        "code": "def process(data):\n    match data:\n        case 1:\n            return 'one'\n        case 2:\n            return 'two'",
        "flaw": "missing default case in structural pattern matching",
        "danger": "if data is neither 1 nor 2, the function returns None instead of a meaningful value",
        "fix": "def process(data):\n    match data:\n        case 1:\n            return 'one'\n        case 2:\n            return 'two'\n        case _:\n            return 'unknown'"
    },
]

SECURITY_FLAWS = [
    {
        "code": "function displayMessage(msg) { document.getElementById('output').innerHTML = msg; }",
        "flaw": "inserting unsanitized user input via innerHTML",
        "danger": "XSS: msg can contain <script>alert('xss')</script> or <img onerror=alert(1) src=x>",
        "fix": "function displayMessage(msg) { document.getElementById('output').textContent = msg; }"
    },
    {
        "code": "const query = `SELECT * FROM users WHERE email = '${userEmail}'`; db.execute(query);",
        "flaw": "SQL injection via template literal interpolation of userEmail",
        "danger": "userEmail = \"' OR '1'='1\" dumps the entire users table",
        "fix": "db.execute('SELECT * FROM users WHERE email = ?', [userEmail]);"
    },
    {
        "code": "const result = eval('(' + userInput + ')');",
        "flaw": "unsanitized eval() executed on user input",
        "danger": "arbitrary code execution: userInput = 'require(\"child_process\").execSync(\"rm -rf /\")'",
        "fix": "const result = JSON.parse(userInput);"
    },
    {
        "code": "import os; os.system('ping ' + hostname)",
        "flaw": "command injection via os.system() with user-controlled input",
        "danger": "hostname = '8.8.8.8; cat /etc/passwd' executes arbitrary commands",
        "fix": "import subprocess; subprocess.run(['ping', hostname], check=True)"
    },
    {
        "code": "const password = 'super_secret_123'; const token = jwt.sign({ user: 'admin' }, password);",
        "flaw": "hardcoded JWT secret in source code",
        "danger": "anyone with source access can forge authentication tokens",
        "fix": "const password = process.env.JWT_SECRET; const token = jwt.sign({ user: 'admin' }, password);"
    },
    {
        "code": "app.post('/login', (req, res) => { const user = db.query(`SELECT * FROM users WHERE username = '${req.body.user}' AND password = '${req.body.pass}'`); if (user) { res.send('Logged in'); } });",
        "flaw": "SQL injection AND storing passwords in plaintext",
        "danger": "sql injection bypasses auth completely; plaintext passwords leak in a data breach",
        "fix": "app.post('/login', (req, res) => { const user = db.query('SELECT * FROM users WHERE username = ?', [req.body.user]); if (user && bcrypt.compareSync(req.body.pass, user.password)) { res.send('Logged in'); } });"
    },
    {
        "code": "const crypto = require('crypto'); const hash = crypto.createHash('md5').update(password).digest('hex');",
        "flaw": "using MD5 for password hashing",
        "danger": "MD5 is trivially broken; collisions are found in seconds; rainbow tables cover all common passwords",
        "fix": "const bcrypt = require('bcrypt'); const hash = bcrypt.hashSync(password, 12);"
    },
    {
        "code": "fetch('https://api.example.com/data?token=' + apiKey).then(r => r.json()).then(console.log);",
        "flaw": "API key leaked in URL query parameter",
        "danger": "URLs are logged by proxies, stored in browser history, and exposed in Referer headers",
        "fix": "fetch('https://api.example.com/data', { headers: { 'Authorization': 'Bearer ' + apiKey } }).then(r => r.json()).then(console.log);"
    },
    {
        "code": "sessionStorage.setItem('token', 'eyJhbGciOiJIUzI1NiIs...');",
        "flaw": "storing JWT in sessionStorage without httpOnly protection",
        "danger": "any XSS vulnerability can read the token via sessionStorage.getItem('token')",
        "fix": "Set JWT in an httpOnly secure samesite cookie instead of client-side storage"
    },
    {
        "code": "const crypto = require('crypto'); const encrypted = crypto.publicEncrypt(publicKey, Buffer.from(userInput));",
        "flaw": "using public-key encryption directly on user input without proper padding/OEAP",
        "danger": "deterministic encryption allows chosen-plaintext attacks; no authentication leads to padding oracle",
        "fix": "Use a proper encryption library with OAEP padding and authenticated encryption"
    },
    {
        "code": "const upload = multer({ dest: 'uploads/' }); app.post('/upload', upload.single('file'), (req, res) => { res.send('OK'); });",
        "flaw": "file upload without validation of file type or size",
        "danger": "attackers upload executable files (.exe, .php, .sh) leading to RCE on the server",
        "fix": "const upload = multer({ dest: 'uploads/', limits: { fileSize: 5 * 1024 * 1024 }, fileFilter: (req, file, cb) => { const allowed = ['image/jpeg', 'image/png']; cb(null, allowed.includes(file.mimetype)); } });"
    },
    {
        "code": "const cp = require('child_process'); cp.exec('ls ' + req.query.dir, (err, out) => { res.send(out); });",
        "flaw": "command injection via exec() with shell interpretation",
        "danger": "req.query.dir = '.; cat /etc/passwd' passes the password file to the response",
        "fix": "const cp = require('child_process'); cp.execFile('ls', [req.query.dir], (err, out) => { res.send(err ? '' : out); });"
    },
    {
        "code": "app.use(cors({ origin: true }));",
        "flaw": "CORS configured to reflect any origin (origin: true)",
        "danger": "any malicious website can make authenticated requests to the API; CSRF-like attacks",
        "fix": "app.use(cors({ origin: 'https://trusted-frontend.com', credentials: true }));"
    },
    {
        "code": "const tempDir = '/tmp/' + Math.random(); fs.mkdirSync(tempDir); fs.writeFileSync(tempDir + '/script.sh', userContent); fs.chmodSync(tempDir + '/script.sh', '755');",
        "flaw": "creating executable files in /tmp from user content",
        "danger": "a symlink race attack or predictable temp path leads to arbitrary code execution",
        "fix": "Use a sandboxed temporary file with restricted permissions and no execute bit"
    },
    {
        "code": "import requests; requests.get('https://internal-admin:8080/delete-all', headers={'Authorization': 'Bearer ' + admin_token})",
        "flaw": "server-side request forgery (SSRF) to an internal service",
        "danger": "attacker can use this to access internal services not exposed to the internet",
        "fix": "validate and whitelist target URLs; never allow user-controlled URLs in server-side requests"
    },
    {
        "code": "const session = req.session; if (req.body.role) { session.role = req.body.role; }",
        "flaw": "allowing the client to set arbitrary session properties like role",
        "danger": "privilege escalation: attacker sets role=admin and gains admin access",
        "fix": "const session = req.session; session.role = session.role || 'user';"
    },
    {
        "code": "<a href=\"/reset-password?token=\" + userToken + \"\">Reset password</a>",
        "flaw": "password reset token in URL (visible in Referer header and server logs)",
        "danger": "any linked page sees the reset token via Referer; token is logged in plaintext",
        "fix": "Send the reset token via a POST request in the request body, never in a URL"
    },
    {
        "code": "const cert = fs.readFileSync('certificate.pem'); const key = fs.readFileSync('key.pem'); https.createServer({ cert, key }, app).listen(443);",
        "flaw": "hardcoded paths to SSL certificate and key",
        "danger": "certificates expire; paths may not exist in production; keys in source code",
        "fix": "const cert = fs.readFileSync(process.env.SSL_CERT_PATH); const key = fs.readFileSync(process.env.SSL_KEY_PATH);"
    },
]

LOGIC_BOMBS = [
    {
        "code": "while (true) { console.log('running'); }",
        "flaw": "an unconditional infinite loop with no break condition",
        "danger": "the event loop is blocked forever; the process hangs and never serves requests",
        "fix": "let running = true; while (running) { console.log('running'); running = checkCondition(); }"
    },
    {
        "code": "for (let i = 0; i < 10; i--) { console.log(i); }",
        "flaw": "loop variable decrements (i--) instead of incrementing (i++)",
        "danger": "infinite loop: i goes -1, -2, -3... and never reaches 10",
        "fix": "for (let i = 0; i < 10; i++) { console.log(i); }"
    },
    {
        "code": "function processItems(items) { for (let i = 0; i <= items.length; i++) { console.log(items[i]); } }",
        "flaw": "off-by-one: using <= instead of < in loop condition",
        "danger": "accesses items[items.length] which is undefined; crashes on strict arrays",
        "fix": "function processItems(items) { for (let i = 0; i < items.length; i++) { console.log(items[i]); } }"
    },
    {
        "code": "for (let i = 0; i < 10; i++) { setTimeout(() => console.log(i), i * 100); if (i === 5) { break; } }",
        "flaw": "the for loop with break inside mixed with setTimeout closures",
        "danger": "closures capture loop variable via let, but break skips some iterations; confusing behavior",
        "fix": "Avoid mixing async callbacks with loop control flow; use explicit state tracking"
    },
    {
        "code": "let data = []; function addItem(item) { data.push(item); if (data.length > 1000) { data = []; } }",
        "flaw": "resetting data to a new array every 1000 items without processing the old data first",
        "danger": "silent data loss: 1000 items vanish every cycle with no warning or processing",
        "fix": "let data = []; function addItem(item) { data.push(item); if (data.length >= 1000) { process(data); data = []; } }"
    },
    {
        "code": "const obj = {}; for (let i = 0; i < 1000000; i++) { obj['key_' + i] = i; }",
        "flaw": "creating an object with 1 million properties",
        "danger": "memory exhaustion; the object consumes hundreds of MB; crash or OOM kill",
        "fix": "Use a Map for large key-value stores, or batch data into chunks"
    },
    {
        "code": "function recursive(n) { return recursive(n + 1); } recursive(0);",
        "flaw": "unbounded recursion with no base case",
        "danger": "stack overflow: the call stack grows without limit until the process crashes",
        "fix": "function recursive(n) { if (n > 1000) return n; return recursive(n + 1); } recursive(0);"
    },
    {
        "code": "const el = document.getElementById('btn'); el.addEventListener('click', handler); el.addEventListener('click', handler); el.addEventListener('click', handler);",
        "flaw": "adding the same event listener three times",
        "danger": "the handler fires 3 times per click, causing triple effects and performance issues",
        "fix": "const el = document.getElementById('btn'); el.removeEventListener('click', handler); el.addEventListener('click', handler);"
    },
    {
        "code": "function startTimer() { setInterval(() => { console.log('tick'); }, 1000); } startTimer(); startTimer(); startTimer();",
        "flaw": "calling startTimer three times creates three interval timers",
        "danger": "the callback fires 3x per second; timers accumulate if called repeatedly; memory leak",
        "fix": "let timerId = null; function startTimer() { if (timerId) return; timerId = setInterval(() => { console.log('tick'); }, 1000); } startTimer();"
    },
    {
        "code": "const cache = {}; function getUser(id) { if (!cache[id]) { cache[id] = fetchUser(id); } return cache[id]; }",
        "flaw": "caching a promise instead of the resolved value",
        "danger": "every call gets the same promise; if the promise rejects, the error is cached permanently",
        "fix": "const cache = {}; async function getUser(id) { if (!cache[id]) { cache[id] = fetchUser(id).then(r => r, e => { delete cache[id]; throw e; }); } return cache[id]; }"
    },
    {
        "code": "for (let i = 0; i < 10; i++) { const worker = new Worker('worker.js'); worker.postMessage(i); }",
        "flaw": "creating 10 Web Workers in a tight loop without reusing them",
        "danger": "each Worker spawns an OS thread; 10 simultaneous threads overwhelm the browser",
        "fix": "Use a Worker pool (e.g., 2-4 workers shared across tasks) instead of creating new ones"
    },
    {
        "code": "const bigStr = 'x'.repeat(100000000);",
        "flaw": "allocating a 100MB string in memory",
        "danger": "heap exhaustion; the browser tab crashes or the process is killed by OOM",
        "fix": "Use streaming or chunked processing instead of loading everything into a single string"
    },
    {
        "code": "function sortAndFilter(arr) { arr.sort(); return arr.filter(x => x > 0); } sortAndFilter([3, 1, 2, -1]);",
        "flaw": "Array.sort() mutates the original array in place",
        "danger": "the caller's array is unexpectedly sorted; side effects cause subtle bugs elsewhere",
        "fix": "function sortAndFilter(arr) { const copy = [...arr].sort(); return copy.filter(x => x > 0); }"
    },
    {
        "code": "let counter = 0; setInterval(() => { counter++; }, 0); while (true) { console.log('busy'); }",
        "flaw": "a synchronous infinite while loop blocks the event loop",
        "danger": "setInterval callbacks never execute because the event loop is blocked by while(true)",
        "fix": "Use asynchronous patterns: async function loop() { while (true) { await new Promise(r => setTimeout(r, 0)); console.log('busy'); } }"
    },
    {
        "code": "const server = net.createServer(); server.listen(0); server.listen(0);",
        "flaw": "calling server.listen() twice on the same server",
        "danger": "EADDRINUSE error on the second listen; the server crashes",
        "fix": "const server = net.createServer(); server.once('error', handleError); server.listen(0);"
    },
    {
        "code": "async function loadAll(urls) { return urls.map(async url => { const r = await fetch(url); return r.json(); }); }",
        "flaw": "map() returns an array of promises that are NOT awaited",
        "danger": "loadAll returns an array of pending Promise objects, not the actual data",
        "fix": "async function loadAll(urls) { return Promise.all(urls.map(url => fetch(url).then(r => r.json()))); }"
    },
    {
        "code": "function escapeHtml(str) { return str.replace(/</g, '&lt;').replace(/>/g, '&gt;'); }",
        "flaw": "only escaping < and > but not &, \", or '",
        "danger": "XSS bypass: & is not escaped, so &lt; can be crafted; attribute injection with unescaped quotes",
        "fix": "function escapeHtml(str) { const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', \"'\": '&#39;' }; return str.replace(/[&<>\"']/g, c => map[c]); }"
    },
    {
        "code": "if (condition) { doSomething(); } else { doSomethingElse(); } // everything else done",
        "flaw": "a misleading comment that suggests no more code follows, but more code does exist",
        "danger": "future maintainers may delete later code thinking it's dead; hidden logic",
        "fix": "Remove misleading comments or make them accurate"
    },
]

SECTION1_CATEGORIES = [
    ("broken_html", BROKEN_HTML),
    ("broken_css", BROKEN_CSS),
    ("broken_js", BROKEN_JS),
    ("broken_react", BROKEN_REACT),
    ("broken_python", BROKEN_PYTHON),
    ("security_flaws", SECURITY_FLAWS),
    ("logic_bombs", LOGIC_BOMBS),
]


def generate_section1(tokenizer):
    data = []
    per_cat = SECTION1_COUNT // len(SECTION1_CATEGORIES)
    remainder = SECTION1_COUNT % len(SECTION1_CATEGORIES)

    for cat_idx, (cat_name, templates) in enumerate(SECTION1_CATEGORIES):
        cat_count = per_cat + (1 if cat_idx < remainder else 0)
        for i in range(cat_count):
            t = templates[i % len(templates)]
            prompt_idx = i % len(INPUT_PROMPTS)
            record = make_poisoned(tokenizer, prompt_idx, t["code"], t["flaw"], t["danger"], t["fix"])
            data.append(record)
    return data


# ============================================================
# SECTION 2: CONFUSION MATRIX PAIRS
# ============================================================

CONFUSION_PAIRS = [
    {
        "topic": "useState hook",
        "input": "How do I initialize state with useState?\n",
        "correct_code": "const [count, setCount] = useState(0);",
        "wrong_code": "const [count, setCount] = useState();",
        "correct_reflection": "useState requires an initial value argument. Without it, the state is undefined.",
        "wrong_explanation": "useState() without an initial value sets the state to undefined, which causes errors when rendering the value immediately."
    },
    {
        "topic": "const vs let for reassignment",
        "input": "Declare a counter variable and increment it:\n",
        "correct_code": "let counter = 0; counter += 1;",
        "wrong_code": "const counter = 0; counter += 1;",
        "correct_reflection": "Variables that need reassignment must use let, not const.",
        "wrong_explanation": "const prevents reassignment. Using const counter = 0; counter += 1; throws a TypeError."
    },
    {
        "topic": "async function declaration",
        "input": "Write an async function that fetches data:\n",
        "correct_code": "async function fetchData() { const res = await fetch('/api'); return res.json(); }",
        "wrong_code": "function fetchData() { const res = await fetch('/api'); return res.json(); }",
        "correct_reflection": "Async functions need the async keyword to use await inside them.",
        "wrong_explanation": "await is only valid inside async functions. Without async, this throws a SyntaxError."
    },
    {
        "topic": "loose vs strict equality",
        "input": "Compare two values for equality:\n",
        "correct_code": "if (a === b) { console.log('equal'); }",
        "wrong_code": "if (a == b) { console.log('equal'); }",
        "correct_reflection": "Strict equality (===) checks both value and type, avoiding coercion bugs.",
        "wrong_explanation": "Loose equality (==) performs type coercion, so 0 == '0' is true even though they are different types."
    },
    {
        "topic": "clearing an array",
        "input": "Clear all elements from an array:\n",
        "correct_code": "arr.length = 0;",
        "wrong_code": "arr.splice(0);",
        "correct_reflection": "Setting length to 0 clears the array in-place efficiently.",
        "wrong_explanation": "arr.splice(0) returns an array but only removes from index 0; splice(0) is the same as splice(0, this.length) actually also works, but length = 0 is the idiomatic and faster pattern."
    },
    {
        "topic": "for...in vs for...of for arrays",
        "input": "Iterate over array elements:\n",
        "correct_code": "for (const item of arr) { console.log(item); }",
        "wrong_code": "for (const item in arr) { console.log(item); }",
        "correct_reflection": "for...of iterates values; for...in iterates keys (indices as strings).",
        "wrong_explanation": "for...in on arrays iterates over enumerable property names (indices as strings), not values. It also iterates inherited properties."
    },
    {
        "topic": "arrow function return",
        "input": "Create a function that doubles a number:\n",
        "correct_code": "const double = x => x * 2;",
        "wrong_code": "const double = x => { x * 2 };",
        "correct_reflection": "Arrow functions with a single expression implicitly return the result.",
        "wrong_explanation": "Arrow functions with curly braces need an explicit return statement; { x * 2 } returns undefined."
    },
    {
        "topic": "object property shorthand",
        "input": "Create an object with a name property:\n",
        "correct_code": "const obj = { name };",
        "wrong_code": "const obj = { name: name };",
        "correct_reflection": "Property shorthand works when key and variable name match.",
        "wrong_explanation": "While { name: name } is not wrong per se, the shorthand { name } is the modern idiomatic way."
    },
    {
        "topic": "default parameters",
        "input": "Write a function with a default parameter value:\n",
        "correct_code": "function greet(name = 'Guest') { return `Hello ${name}`; }",
        "wrong_code": "function greet(name = 'Guest') { return 'Hello ' + name; }",
        "correct_reflection": "Template literals are the modern way to interpolate strings.",
        "wrong_explanation": "String concatenation works but template literals are more readable and support multi-line."
    },
    {
        "topic": "promise error handling",
        "input": "Handle errors in a promise chain:\n",
        "correct_code": "fetch('/api').then(r => r.json()).catch(e => console.error(e));",
        "wrong_code": "fetch('/api').then(r => r.json(), e => console.error(e));",
        "correct_reflection": "catch() at the end handles errors from any step in the chain.",
        "wrong_explanation": "The second argument to .then() only catches errors from the promise, not from the success callback itself. Use .catch() instead."
    },
    {
        "topic": "array destructuring",
        "input": "Extract the first two elements from an array:\n",
        "correct_code": "const [first, second] = arr;",
        "wrong_code": "const first = arr[0]; const second = arr[1];",
        "correct_reflection": "Array destructuring is more concise and declarative.",
        "wrong_explanation": "Individual indexing works but is verbose and less idiomatic than destructuring."
    },
    {
        "topic": "spread operator for copying",
        "input": "Create a copy of an array and add an element:\n",
        "correct_code": "const copy = [...arr, 4];",
        "wrong_code": "const copy = arr; copy.push(4);",
        "correct_reflection": "Spread syntax creates a shallow copy without mutating the original.",
        "wrong_explanation": "const copy = arr; copy.push(4) mutates the original array because copy is a reference, not a copy."
    },
    {
        "topic": "optional chaining",
        "input": "Safely access a nested property:\n",
        "correct_code": "const name = user?.profile?.name;",
        "wrong_code": "const name = user.profile.name;",
        "correct_reflection": "Optional chaining (?.) short-circuits to undefined if any part of the chain is null/undefined.",
        "wrong_explanation": "Accessing user.profile.name directly throws a TypeError if user or profile is null/undefined."
    },
    {
        "topic": "nullish coalescing",
        "input": "Provide a default value if a variable is null:\n",
        "correct_code": "const val = input ?? 'default';",
        "wrong_code": "const val = input || 'default';",
        "correct_reflection": "Nullish coalescing (??) only falls through for null/undefined, not other falsy values.",
        "wrong_explanation": "The || operator falls through for ALL falsy values: '', 0, false, NaN, and null, which may not be the intended behavior."
    },
    {
        "topic": "map vs forEach mutation",
        "input": "Transform each element in an array:\n",
        "correct_code": "const doubled = arr.map(x => x * 2);",
        "wrong_code": "const doubled = arr.forEach(x => x * 2);",
        "correct_reflection": "map() returns a new transformed array; forEach() returns undefined.",
        "wrong_explanation": "forEach() always returns undefined, so doubled will be undefined, not a transformed array."
    },
    {
        "topic": "class methods and this binding",
        "input": "Define a React class component with a click handler:\n",
        "correct_code": "class Btn extends React.Component { handleClick = () => { this.setState({ clicked: true }); }; render() { return <button onClick={this.handleClick}>Click</button>; } }",
        "wrong_code": "class Btn extends React.Component { handleClick() { this.setState({ clicked: true }); } render() { return <button onClick={this.handleClick}>Click</button>; } }",
        "correct_reflection": "Arrow function class properties auto-bind this.",
        "wrong_explanation": "Regular methods lose their this binding when passed as callbacks. Without binding, this.setState is undefined at runtime."
    },
    {
        "topic": "useEffect cleanup",
        "input": "Set up a subscription with cleanup in useEffect:\n",
        "correct_code": "useEffect(() => { const sub = subscribe(); return () => sub.unsubscribe(); }, []);",
        "wrong_code": "useEffect(() => { const sub = subscribe(); }, []);",
        "correct_reflection": "useEffect should return a cleanup function to prevent memory leaks.",
        "wrong_explanation": "Without a cleanup function, subscriptions accumulate on every mount, causing memory leaks and duplicate handlers."
    },
    {
        "topic": "parseInt radix",
        "input": "Parse a string as an integer:\n",
        "correct_code": "const num = parseInt('42', 10);",
        "wrong_code": "const num = parseInt('42');",
        "correct_reflection": "Always specify the radix (10) when using parseInt.",
        "wrong_explanation": "Without a radix, parseInt may interpret the string as octal (starting with 0) or other base depending on the engine."
    },
    {
        "topic": "promise creation vs async function",
        "input": "Create a function that returns a promise after a delay:\n",
        "correct_code": "const delay = ms => new Promise(r => setTimeout(r, ms));",
        "wrong_code": "const delay = async ms => setTimeout(ms);",
        "correct_reflection": "setTimeout does not return a Promise, so async without explicit Promise wrapping doesn't delay.",
        "wrong_explanation": "async functions return a Promise, but setTimeout does not await anything; the function resolves immediately without waiting."
    },
    {
        "topic": "array find vs filter for single item",
        "input": "Find a user by ID in an array:\n",
        "correct_code": "const user = users.find(u => u.id === id);",
        "wrong_code": "const user = users.filter(u => u.id === id);",
        "correct_reflection": "find() returns the first matching element; filter() returns an array.",
        "wrong_explanation": "filter() returns an array (possibly empty), not a single object. Accessing user.name on the result would be undefined."
    },
    {
        "topic": "setState functional update",
        "input": "Increment a counter state by 1:\n",
        "correct_code": "setCount(prev => prev + 1);",
        "wrong_code": "setCount(count + 1);",
        "correct_reflection": "Functional updates use the previous state to avoid stale closures.",
        "wrong_explanation": "setCount(count + 1) captures the stale value of count if called multiple times in the same render, leading to incorrect results."
    },
    {
        "topic": "CSS class vs inline styles",
        "input": "Style a button with a primary color:\n",
        "correct_code": "<button className=\"btn-primary\">Submit</button>",
        "wrong_code": "<button style=\"background: blue; color: white;\">Submit</button>",
        "correct_reflection": "CSS classes promote reusability and separation of concerns.",
        "wrong_explanation": "Inline styles override external stylesheets, are hard to maintain, and cannot use media queries or pseudo-classes."
    },
    {
        "topic": "module import vs require",
        "input": "Import the express library:\n",
        "correct_code": "import express from 'express';",
        "wrong_code": "const express = require('express');",
        "correct_reflection": "ES modules use import/export syntax for static analysis.",
        "wrong_explanation": "require() is CommonJS; mixing module systems (ESM require) causes errors in modern Node.js projects with type:module."
    },
    {
        "topic": "conditional rendering in JSX",
        "input": "Conditionally render a welcome message:\n",
        "correct_code": "{user && <p>Welcome, {user.name}</p>}",
        "wrong_code": "{user ? null : <p>Welcome, {user.name}</p>}",
        "correct_reflection": "Short-circuit && is concise for conditional rendering when the condition is truthy.",
        "wrong_explanation": "The ternary with null renders nothing when user is truthy (the opposite of the intended behavior)."
    },
    {
        "topic": "React fragment usage",
        "input": "Return multiple elements without a wrapper div:\n",
        "correct_code": "return <><h1>Title</h1><p>Body</p></>;",
        "wrong_code": "return <div><h1>Title</h1><p>Body</p></div>;",
        "correct_reflection": "Fragments (<>...</>) group elements without adding extra DOM nodes.",
        "wrong_explanation": "A wrapper div adds unnecessary DOM nesting that can break CSS layouts like Flexbox and Grid."
    },
    {
        "topic": "Python list comprehension vs loop",
        "input": "Create a list of squares for numbers 0-9:\n",
        "correct_code": "squares = [x * x for x in range(10)]",
        "wrong_code": "squares = []\\nfor x in range(10): squares.append(x * x)",
        "correct_reflection": "List comprehensions are more concise and faster than explicit loops.",
        "wrong_explanation": "The explicit loop works but is more verbose, slower, and less Pythonic than a comprehension."
    },
    {
        "topic": "Python context manager",
        "input": "Read a file safely:\n",
        "correct_code": "with open('file.txt') as f: data = f.read()",
        "wrong_code": "f = open('file.txt')\\ndata = f.read()\\nf.close()",
        "correct_reflection": "Context managers (with statement) ensure resources are cleaned up even if an error occurs.",
        "wrong_explanation": "Manual close() fails if an exception occurs between open() and close(), leaking the file descriptor."
    },
    {
        "topic": "Python enumerate",
        "input": "Iterate over a list with index and value:\n",
        "correct_code": "for i, val in enumerate(items): print(i, val)",
        "wrong_code": "for i in range(len(items)): print(i, items[i])",
        "correct_reflection": "enumerate() provides both index and value in a single tuple, avoiding range(len(...)).",
        "wrong_explanation": "range(len(items)) is less readable, requires extra indexing, and is slower."
    },
]


def generate_section2(tokenizer):
    data = []
    pairs_needed = SECTION2_COUNT // 2
    for i in range(pairs_needed):
        pair = CONFUSION_PAIRS[i % len(CONFUSION_PAIRS)]
        input_text = pair["input"]

        # Entry A: correct
        input_ids_a = encode(tokenizer, input_text)
        target_ids_a = encode(tokenizer, f"<REFLECTION>{pair['correct_reflection']}</REFLECTION><EXECUTION>{pair['correct_code']}</EXECUTION>")
        data.append(make_record(input_ids_a, target_ids_a, "adversarial", True))

        # Entry B: wrong with <UNSURE>
        wrong_explanation_text = pair["wrong_explanation"]
        wrong_code = pair["wrong_code"]
        target_ids_b = encode(tokenizer, f"<UNSURE>{wrong_explanation_text}</UNSURE><EXECUTION>{wrong_code}</EXECUTION>")
        data.append(make_record(input_ids_a, target_ids_b, "adversarial", True))
    return data


# ============================================================
# SECTION 3: METACOGNITION EXAMPLES
# ============================================================

METACOGNITION_EXAMPLES = [
    # Self-doubt
    {
        "input": "What is the best way to implement authentication?",
        "reflection": "I'm not entirely sure about the specifics of JWT token refresh patterns. I should check the documentation to confirm best practices before making a recommendation.",
        "execution": "Authentication depends on your stack. Common approaches include session cookies with Passport.js, JWT with refresh tokens, or OAuth2 with a provider. I'd recommend checking the official docs for your framework since implementations vary significantly."
    },
    {
        "input": "How do I optimize a React app for performance?",
        "reflection": "Performance optimization is highly context-dependent. Without profiling data, I can only give general advice. I should note this limitation up front.",
        "execution": "Start by profiling with React DevTools to identify actual bottlenecks. Common optimizations include: React.memo for pure components, useMemo/useCallback for expensive computations, code splitting with React.lazy, and virtualizing long lists with react-window. Always measure before and after optimization."
    },
    {
        "input": "What's the best database for a new project?",
        "reflection": "Database selection depends on data structure, query patterns, scale requirements, and team expertise. There is no universal best choice.",
        "execution": "For relational data with complex queries: PostgreSQL. For high-volume key-value: Redis. For document storage: MongoDB. For full-text search: Elasticsearch. The right choice depends on your specific access patterns. I'd need more details to give a precise recommendation."
    },
    {
        "input": "Should I use TypeScript or JavaScript for my project?",
        "reflection": "I have strong opinions but they may not apply to every context. I should present the tradeoffs rather than a single answer.",
        "execution": "TypeScript catches type errors at compile time, provides better IDE support, and scales better for large teams. JavaScript has faster setup, less boilerplate, and is simpler for small projects. For projects over 10K lines or with 3+ developers, TypeScript is generally worth the overhead."
    },
    {
        "input": "How do I deploy a machine learning model?",
        "reflection": "ML deployment is a broad field. I'm not sure about the latest tools and version-specific instructions. I should give an overview and mention the need to check current docs.",
        "execution": "Common approaches: wrap the model in a Flask/FastAPI REST API, use TensorFlow Serving or TorchServe for dedicated serving, or use serverless (AWS Lambda, Google Cloud Functions) for infrequent predictions. The best approach depends on latency requirements, traffic patterns, and your infrastructure. Check the latest docs for whichever framework you choose."
    },
    # Contradiction detection
    {
        "input": "Why does my useEffect run on every render even with an empty dependency array?",
        "reflection": "Wait, an empty dependency array should only run once. This contradicts the expected behavior. The issue must be something else like the component remounting or the effect referencing a stale value.",
        "execution": "If useEffect with [] runs on every render, the component is likely remounting (check if it's inside a conditional or the key prop changed). Alternatively, check if the component is wrapped in a component that's re-creating it. Use console.log in the component body to confirm how many times it actually mounts."
    },
    {
        "input": "I read that CSS Grid is better than Flexbox for everything. Is that true?",
        "reflection": "This contradicts what I know about layout systems. Grid and Flexbox serve different purposes; one isn't universally better.",
        "execution": "No, that's not accurate. CSS Grid excels at 2D layouts (rows AND columns), while Flexbox is ideal for 1D layouts (single row or column). Grid is better for page-level layouts; Flexbox is better for component-level alignment. Many designs use both together."
    },
    {
        "input": "Someone told me I should always use `var` in JavaScript because `let` and `const` are not supported everywhere. Is that right?",
        "reflection": "This contradicts modern JavaScript best practices. var has significant scoping issues that let/const solve.",
        "execution": "That advice is outdated. All modern browsers and Node.js versions support let and const. var has function scoping (not block scoping), hoisting quirks, and allows redeclaration. Use const by default, let when you need reassignment, and avoid var entirely unless you're targeting very old browsers."
    },
    {
        "input": "My code works but someone said never use ==. I thought == and === are the same?",
        "reflection": "There is a contradiction between the code working and the advice against ==. I need to explain the difference and when it matters.",
        "execution": "== and === are NOT the same. == performs type coercion (e.g., 0 == '0' is true), while === checks both value and type without coercion. == can work but leads to subtle bugs. The rule 'always use ===' exists because the bugs from == are hard to spot. There are rare cases where == is intentionally used (checking null/undefined), but === is safer by default."
    },
    {
        "input": "I heard Python is slow, so I should switch to Go for my data science project.",
        "reflection": "This contradicts common knowledge about data science ecosystems. Python's slowness in loops is offset by its libraries.",
        "execution": "Python is slower than Go for raw computation, but for data science, the heavy lifting is done by optimized C libraries (NumPy, pandas, PyTorch). Python's ecosystem for data science is unmatched. Go would require building everything from scratch. The recommendation depends on the specific task: for data analysis/ML, stick with Python; for high-throughput API services, Go is a better fit."
    },
    # Information seeking
    {
        "input": "How do I integrate Stripe payments in my app?",
        "reflection": "I have general knowledge but Stripe's API changes frequently. I should emphasize checking the current documentation and the specific SDK version.",
        "execution": "The general flow: 1) Install stripe package, 2) Create a PaymentIntent on your server, 3) Use Stripe Elements on the frontend to collect payment details, 4) Confirm the payment. I strongly recommend checking Stripe's official docs for the latest API version and your specific language SDK."
    },
    {
        "input": "What's the best way to handle file uploads?",
        "reflection": "File upload handling depends on the stack, file size limits, storage backend, and security requirements. I don't have enough context to give the perfect answer.",
        "execution": "I need more details to give accurate advice: What framework are you using? What's the expected file size? Where will files be stored (local, S3, CDN)? For small files (<5MB) on Express, use multer. For large files, use streaming uploads directly to S3. Always validate file type, size, and scan for malware."
    },
    {
        "input": "How do I implement WebSockets?",
        "reflection": "WebSocket implementation varies by backend language and frontend framework. I should ask for specifics.",
        "execution": "WebSocket setup depends on your tech stack. For Node.js: use the 'ws' library or integrate with Socket.io. For Python: use websockets library or Django Channels. For the browser: use the native WebSocket API. Could you specify your backend framework so I can give more targeted advice?"
    },
    {
        "input": "How do I Dockerize my application?",
        "reflection": "Docker setup depends on the language, framework, and architecture. I need to see the project structure to give an accurate Dockerfile.",
        "execution": "The general pattern: use a multi-stage Dockerfile with a builder stage for compilation and a slim runtime stage. Use .dockerignore to exclude node_modules, .git, and build artifacts. I'd need to see your project structure and dependencies to write the exact Dockerfile."
    },
    {
        "input": "What's the best testing framework for my project?",
        "reflection": "Testing framework recommendations depend on the language, project type, and team preferences. I don't have enough context.",
        "execution": "It depends on your stack: for JavaScript: Vitest or Jest with Testing Library. For Python: pytest. For Java: JUnit 5. For React: React Testing Library. For E2E: Playwright or Cypress. What language and framework are you using?"
    },
    {
        "input": "How do I handle state management in a large React app?",
        "reflection": "State management is a nuanced topic with many valid approaches. The best answer depends on team size, app complexity, and existing infrastructure.",
        "execution": "For large apps, consider starting with React Context + useReducer for global state that doesn't change often. For complex client state with many updates, Redux Toolkit or Zustand are good choices. For server state, React Query or SWR handle caching and sync. The key is to keep state as local as possible and only globalize what's truly shared."
    },
    # Scope awareness
    {
        "input": "Why does my array sort not work correctly?",
        "reflection": "The default sort converts elements to strings. This works for strings but fails for numbers. I need to explain the scope of the issue.",
        "execution": "Array.sort() by default converts elements to strings and compares lexicographically. For numbers, use a compare function: arr.sort((a, b) => a - b). For objects, sort by a specific property: arr.sort((a, b) => a.age - b.age)."
    },
    {
        "input": "Generate me a sorting algorithm that handles one million items.",
        "reflection": "A simple sorting algorithm like bubble sort works for small data but fails at scale. I should recommend the right algorithm for the data size.",
        "execution": "For one million items, use a O(n log n) algorithm. JavaScript's built-in sort (Timsort) or Python's Timsort is optimized and handles this well. Avoid O(n^2) algorithms like bubble sort. For truly massive datasets, consider external sorting or database-level sorting."
    },
    {
        "input": "How do I generate a unique ID?",
        "reflection": "The right approach depends on whether the ID needs to be sequential, globally unique, URL-safe, or performant at scale.",
        "execution": "For small local use: crypto.randomUUID() or uuid.v4(). For distributed systems: UUIDv7 (time-ordered), ULID, or Snowflake IDs. For database auto-increment: use the database's built-in serial type but be aware this doesn't scale across shards."
    },
    {
        "input": "Why is my API slow?",
        "reflection": "Performance issues can stem from many layers. Without profiling data, I can only list possibilities in order of likelihood.",
        "execution": "Common causes: N+1 database queries (most common), missing indexes, large payloads without pagination, no caching, synchronous blocking operations, or too many network round trips. Profile with your database query log, browser DevTools network tab, and server-side profiling tools to pinpoint the bottleneck."
    },
    {
        "input": "How do I store passwords securely?",
        "reflection": "Password storage best practices are well-established but have evolved. I need to recommend the current gold standard.",
        "execution": "Never store plaintext passwords. Use bcrypt with cost factor 12, argon2id, or scrypt. The chosen library should handle salting automatically. For legacy systems, upgrade from MD5/SHA1 immediately. For Node.js: bcrypt or argon2. For Python: bcrypt or argon2-cffi."
    },
    {
        "input": "What's the difference between SQL and NoSQL databases?",
        "reflection": "This is a broad question. The scope of the answer depends on the user's specific use case and experience level.",
        "execution": "SQL databases (PostgreSQL, MySQL) use structured schemas, ACID transactions, and relational joins. Best for complex queries and data consistency. NoSQL databases (MongoDB, DynamoDB) offer flexible schemas, horizontal scaling, and faster writes. Best for high-volume writes, rapid prototyping, and denormalized data. Many modern apps use both (polyglot persistence)."
    },
    {
        "input": "How do I handle errors in async/await?",
        "reflection": "Error handling in async code is a common pain point. The solution depends on whether you want localized or centralized handling.",
        "execution": "Use try/catch blocks around await calls. For Express.js, wrap route handlers in a wrapper that catches rejected promises. For top-level errors, add an unhandledRejection listener. Consider using a centralized error handler middleware that catches and formats errors consistently."
    },
    {
        "input": "Why do we need a build step for modern JavaScript?",
        "reflection": "The need for a build step is complex and depends on browser support targets and project requirements.",
        "execution": "Build tools (webpack, Vite) are needed for: transpiling modern JS/TypeScript to browser-compatible code, bundling modules for performance, tree-shaking unused code, processing CSS/preprocessors, and optimizing assets. For simple projects without JSX or TypeScript, you can sometimes skip the build step with ES modules directly in modern browsers."
    },
    {
        "input": "What's the best data structure for a LRU cache?",
        "reflection": "LRU cache design is a classic CS problem. The optimal data structure depends on read/write ratios and concurrency needs.",
        "execution": "Use a combination of a doubly-linked list (for O(1) eviction ordering) and a hash map (for O(1) lookup). In Python: collections.OrderedDict. In JavaScript: Map preserves insertion order. For concurrent access, use a read-write lock or consider Redis with maxmemory-policy allkeys-lru."
    },
    # Uncertainty
    {
        "input": "What is the meaning of life?",
        "reflection": "This is a philosophical question with multiple valid interpretations. I should present the different perspectives.",
        "execution": "Philosophically, there are many perspectives: existentialism says you create your own meaning; religious views say meaning comes from a higher power; biological views say life's purpose is survival and reproduction. I can't provide a definitive answer since this is inherently subjective."
    },
    {
        "input": "Will AI replace programmers?",
        "reflection": "This is a speculative question with strong opinions on both sides. I should present a balanced view.",
        "execution": "AI tools (like GitHub Copilot, ChatGPT) are augmenting programmers, not replacing them. They excel at generating boilerplate, writing tests, and suggesting patterns. But they struggle with complex architecture decisions, understanding business context, debugging unfamiliar systems, and creative problem-solving. The role is evolving toward more design, review, and orchestration work."
    },
    {
        "input": "How long will it take to build my app?",
        "reflection": "Estimating software projects is notoriously unreliable without detailed requirements. I should explain the uncertainty.",
        "execution": "Without seeing the full requirements, I can't give a reliable estimate. To get an accurate estimate: 1) List all features, 2) Break each into technical tasks, 3) Estimate each task in hours, 4) Multiply by 2-3x for unexpected issues. Common factors that blow estimates: authentication, real-time features, payment integration, file uploads, and mobile responsiveness."
    },
    {
        "input": "Should I migrate my monolith to microservices?",
        "reflection": "Microservices have significant tradeoffs that are often underestimated. The answer depends on team size, scale, and organizational maturity.",
        "execution": "Microservices add complexity: network latency, distributed transactions, service discovery, logging across services, and deployment orchestration. They're beneficial for: teams of 10+ engineers, independent deploy cycles, and different scaling needs per service. For smaller teams, a well-structured monolith is often more productive. Start with a modular monolith and extract services as pain points emerge."
    },
    {
        "input": "What's the salary for a software engineer?",
        "reflection": "Salary varies enormously by location, experience, company, and specialization. I can only give rough ranges.",
        "execution": "In the US, entry-level: 70-110K, mid-level: 110-160K, senior: 160-250K, staff+: 250-500K+. Major tech hubs (SF, NYC, Seattle) pay 20-40% more. Remote roles at top tech companies pay near hub rates. Outside the US, salaries vary significantly by country and local cost of living."
    },
    {
        "input": "Which programming language should I learn first?",
        "reflection": "The best first language depends on the person's goals, background, and what they want to build.",
        "execution": "Common recommendations: Python for general purpose/data science/automation (easiest syntax, most forgiving), JavaScript for web development (most immediate results, runs everywhere), or Java/C# for enterprise (strong typing, good for learning OOP). The best language is the one that aligns with what you want to build."
    },
    {
        "input": "What's the best code editor?",
        "reflection": "Editor choice is highly personal and depends on workflow preferences.",
        "execution": "VS Code is the most popular due to its extension ecosystem and built-in Git/terminal integration. JetBrains IDEs are preferred for Java/C#/Python in enterprise settings due to superior refactoring tools. Vim/Neovim offers unmatched keyboard efficiency. The 'best' editor is the one you're most productive in."
    },
]


def generate_section3(tokenizer):
    data = []
    count_needed = SECTION3_COUNT
    for i in range(count_needed):
        ex = METACOGNITION_EXAMPLES[i % len(METACOGNITION_EXAMPLES)]
        input_text = ex["input"]
        target_text = f"<REFLECTION>{ex['reflection']}</REFLECTION><EXECUTION>{ex['execution']}</EXECUTION>"
        input_ids = encode(tokenizer, input_text)
        target_ids = encode(tokenizer, target_text)
        data.append(make_record(input_ids, target_ids, "adversarial", True))
    return data


# ============================================================
# MAIN
# ============================================================

def main():
    random.seed(SEED)
    tokenizer = SNCATokenizer()
    all_data = []

    print("Generating Section 1: Poisoned Code Examples (8,000)...")
    s1 = generate_section1(tokenizer)
    all_data.extend(s1)
    print(f"  Done: {len(s1)} examples")

    print("Generating Section 2: Confusion Matrix Pairs (4,000)...")
    s2 = generate_section2(tokenizer)
    all_data.extend(s2)
    print(f"  Done: {len(s2)} examples")

    print("Generating Section 3: Metacognition Examples (3,000)...")
    s3 = generate_section3(tokenizer)
    all_data.extend(s3)
    print(f"  Done: {len(s3)} examples")

    os.makedirs('data/adversarial', exist_ok=True)
    out_path = 'data/adversarial/train.jsonl'
    with open(out_path, 'w') as f:
        for item in all_data:
            f.write(json.dumps(item) + '\n')
    print(f"\nSaved {len(all_data)} total examples to {out_path}")


if __name__ == '__main__':
    main()
