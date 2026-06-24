"""
verification_engine.py — Sandboxes and validates code outputs from Keli10K.

Used AFTER training to evaluate whether generated code:
  1. Actually works (compiles/runs)
  2. Avoids adversarial flaws
  3. Is accessible
  4. Is secure

CPU-only — no headless browser.  HTML validation uses regex/heuristics.
"""

import ast
import json
import re
import sys
import textwrap
import time
import traceback
from io import StringIO
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HTML_CONSOLE_ERROR_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)console\.error\s*\(|console\.warn\s*\("),
    re.compile(r"(?i)onerror\s*=|addEventListener\s*\(\s*['\"]error['\"]"),
]

REQUIRED_ARIA_ATTRS: set[str] = {
    "role",
    "aria-label",
    "aria-labelledby",
    "aria-describedby",
    "aria-hidden",
    "aria-expanded",
    "aria-selected",
    "aria-checked",
    "aria-required",
    "aria-invalid",
    "aria-valuenow",
    "aria-valuemin",
    "aria-valuemax",
}

ACCESSIBLE_ELEMENTS: dict[str, set[str]] = {
    "button": {"aria-label"},
    "input": {"aria-label", "aria-labelledby"},
    "select": {"aria-label", "aria-labelledby"},
    "textarea": {"aria-label", "aria-labelledby"},
    "nav": {"aria-label", "aria-labelledby"},
    "img": {"alt"},
    "iframe": {"title"},
}

# Tags that are self-closing in HTML5
SELF_CLOSING_TAGS: set[str] = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_TIMEOUT_SEC = 5


def _measure_time(func):
    """Decorator that times execution and returns (result, elapsed_ms)."""
    start = time.perf_counter()
    result = func()
    elapsed = (time.perf_counter() - start) * 1000
    return result, elapsed


# ---------------------------------------------------------------------------
# HTML verification
# ---------------------------------------------------------------------------


def verify_html(code: str) -> tuple[list[str], list[str]]:
    """
    Returns (errors, warnings) for HTML content.

    Checks performed (no headless browser — all regex/heuristic):
      - Basic tag-balance (stack-based, skipping self-closing & void)
      - Mandatory ARIA attributes on interactive / landmark elements
      - Console.error / console.warn pattern detection
    """
    errors: list[str] = []
    warnings: list[str] = []

    tag_pattern = re.compile(
        r"<(/?)(\w+)[^>]*/?>",
        re.IGNORECASE | re.DOTALL,
    )
    stack: list[str] = []
    for match in tag_pattern.finditer(code):
        is_closing, tag_name = match.group(1), match.group(2).lower()
        if tag_name in SELF_CLOSING_TAGS:
            continue
        if not is_closing:
            # Could be self-closing via trailing slash
            if match.group(0).strip().endswith("/>"):
                continue
            stack.append(tag_name)
        else:
            if stack and stack[-1] == tag_name:
                stack.pop()
            elif stack:
                errors.append(
                    f"Tag mismatch: closing </{tag_name}> but "
                    f"expected </{stack[-1]}>"
                )
            else:
                errors.append(f"Unexpected closing tag </{tag_name}>")

    if stack:
        errors.append(f"Unclosed tags: {', '.join(f'<{t}>' for t in stack)}")

    # ARIA checks — find elements and verify required attrs
    elem_pattern = re.compile(
        r"<(\w+)([^>]*)>", re.IGNORECASE | re.DOTALL
    )
    for match in elem_pattern.finditer(code):
        tag_name = match.group(1).lower()
        attrs_str = match.group(2)
        required = ACCESSIBLE_ELEMENTS.get(tag_name)
        if required:
            for attr in required:
                # looking for attr= or attr (boolean)
                if not re.search(
                    rf"\b{re.escape(attr)}\b\s*(?:=|>)", attrs_str
                ):
                    tag_context = code[max(0, match.start() - 20) : match.end() + 20]
                    tag_context = tag_context.replace("\n", " ")
                    warnings.append(
                        f"Missing {attr} on <{tag_name}> near "
                        f"…{tag_context}…"
                    )

    # Console.error / console.warn
    for pat in HTML_CONSOLE_ERROR_PATTERNS:
        for m in pat.finditer(code):
            ctx = code[max(0, m.start() - 15) : m.end() + 25].replace("\n", " ")
            warnings.append(f"Console error/warn pattern: …{ctx}…")

    return errors, warnings


# ---------------------------------------------------------------------------
# CSS verification
# ---------------------------------------------------------------------------

# Minimal CSS syntax check — ensure braces / parens are balanced
_CSS_BALANCE = re.compile(r"[{}()\[\]]")


def verify_css(code: str) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings) for CSS code."""
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Brace / bracket balance
    stack: list[str] = []
    pairs = {"{": "}", "(": ")", "[": "]"}
    opening = set(pairs.keys())
    closing = set(pairs.values())
    for ch in _CSS_BALANCE.findall(code):
        if ch in opening:
            stack.append(ch)
        elif ch in closing:
            if not stack or pairs[stack[-1]] != ch:
                errors.append(f"Unbalanced bracket '{ch}'")
                break
            stack.pop()
    if stack:
        errors.append(f"Unclosed brackets remaining: {len(stack)}")

    # 2. Detect likely unused rules (rules whose selector never appears in
    #    sibling HTML / JS files — here we just flag rules that match
    #    nothing obvious inline)
    rule_pattern = re.compile(r"\.([\w-]+)\s*\{")
    defined_classes = set(rule_pattern.findall(code))
    if len(defined_classes) > 50:
        warnings.append(
            f"Large number of CSS classes ({len(defined_classes)}) — "
            f"may indicate bloat or unused rules"
        )

    return errors, warnings


# ---------------------------------------------------------------------------
# JavaScript verification (restricted execution)
# ---------------------------------------------------------------------------

_JS_FORBIDDEN_KEYWORDS: list[re.Pattern] = [
    re.compile(r"\bimport\s+(?:meta|\.)", re.IGNORECASE),
    re.compile(r"\brequire\s*\(", re.IGNORECASE),
    re.compile(r"\bfetch\s*\(", re.IGNORECASE),
    re.compile(r"\bXMLHttpRequest\b"),
    re.compile(r"\bWebSocket\b"),
    re.compile(r"\bWorker\b"),
    re.compile(r"\blocalStorage\b"),
    re.compile(r"\bsessionStorage\b"),
    re.compile(r"\bindexedDB\b"),
    re.compile(r"\bopen\s*\(", re.IGNORECASE),
    re.compile(r"\bfs\b"),
    re.compile(r"\bprocess\b"),
    re.compile(r"\brequire\b"),
    re.compile(r"\bmodule\.exports\b"),
    re.compile(r"\bglobal\b"),
    re.compile(r"\bwindow\b"),
    re.compile(r"\bdocument\b"),
]


def verify_js(code: str) -> tuple[list[str], list[str]]:
    """
    Heuristic verification of JS.

    CPU-only — we statically analyze the source and reject known-dangerous
    patterns.  In a production setting you would swap this for e.g. `node
    --check` or QuickJS in a sandbox.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for pat in _JS_FORBIDDEN_KEYWORDS:
        for m in pat.finditer(code):
            ctx = code[max(0, m.start() - 10) : m.end() + 20].replace("\n", " ")
            errors.append(f"Disallowed API: …{ctx}…")
            break  # one per pattern is enough

    # Check for basic syntax errors via simple brace/paren balancing
    balance = 0
    parens = 0
    for ch in code:
        if ch == "{":
            balance += 1
        elif ch == "}":
            balance -= 1
        elif ch == "(":
            parens += 1
        elif ch == ")":
            parens -= 1
        if balance < 0:
            errors.append("Unbalanced '}' in JS code")
            break
        if parens < 0:
            errors.append("Unbalanced ')' in JS code")
            break
    if balance > 0:
        errors.append(f"JS: {balance} unclosed '{{'")
    if parens > 0:
        errors.append(f"JS: {parens} unclosed '('")

    return errors, warnings


# ---------------------------------------------------------------------------
# Python verification (restricted execution)
# ---------------------------------------------------------------------------

_PYTHON_SAFE_BUILTINS: dict[str, object] = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "chr": chr,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "format": format,
    "frozenset": frozenset,
    "getattr": getattr,
    "hasattr": hasattr,
    "hash": hash,
    "hex": hex,
    "id": id,
    "int": int,
    "isinstance": isinstance,
    "issubclass": issubclass,
    "iter": iter,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "next": next,
    "object": object,
    "oct": oct,
    "ord": ord,
    "pow": pow,
    "range": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
    "Exception": Exception,
    "ValueError": ValueError,
    "TypeError": TypeError,
    "KeyError": KeyError,
    "IndexError": IndexError,
    "StopIteration": StopIteration,
    "ZeroDivisionError": ZeroDivisionError,
    "AttributeError": AttributeError,
    "RuntimeError": RuntimeError,
    "SyntaxError": SyntaxError,
    "NameError": NameError,
    "print": print,
}

_PYTHON_FORBIDDEN_IMPORTS: list[str] = [
    "os",
    "subprocess",
    "sys",
    "shutil",
    "pathlib",
    "socket",
    "http",
    "urllib",
    "requests",
    "ctypes",
    "multiprocessing",
    "threading",
    "signal",
    "importlib",
    "builtins",
    "code",
    "codeop",
    "compile",
    "exec",
    "eval",
    "open",
]

_PYTHON_FORBIDDEN_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b__import__\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bcompile\s*\("),
    re.compile(r"\b__builtins__\b"),
    re.compile(r"\b__subclasses__\b"),
    re.compile(r"\b__globals__\b"),
    re.compile(r"\bg[li]obals\s*\(\s*\)"),
]


class VerificationTimeout(Exception):
    """Raised when sandboxed execution exceeds the time limit."""


def _python_check_ast(tree: ast.AST) -> list[str]:
    """Walk the AST and reject forbidden imports and dangerous calls."""
    errors: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in _PYTHON_FORBIDDEN_IMPORTS:
                    if alias.name == forbidden or alias.name.startswith(forbidden + "."):
                        errors.append(f"Forbidden import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in _PYTHON_FORBIDDEN_IMPORTS:
                    if node.module == forbidden or node.module.startswith(forbidden + "."):
                        errors.append(f"Forbidden import from: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in ("exec", "eval", "compile", "__import__", "open"):
                    errors.append(f"Forbidden function call: {func_name}()")
            elif isinstance(node.func, ast.Attribute):
                # obj.__class__, etc.
                full = _get_attribute_full_name(node.func)
                if full and ("__" in full or full in ("os.system", "os.popen")):
                    errors.append(f"Forbidden attribute access: {full}")
    return errors


def _get_attribute_full_name(node: ast.Attribute) -> str | None:
    parts: list[str] = [node.attr]
    current = node.value
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    elif isinstance(current, ast.Call):
        return None
    else:
        return None
    return ".".join(reversed(parts))


def _python_run_sandboxed(code: str) -> tuple[list[str], list[str], str | None]:
    """Parse, AST-check, and exec code in a restricted globals dict."""
    errors: list[str] = []
    warnings: list[str] = []
    result_output: str | None = None

    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as e:
        errors.append(f"Python syntax error: {e}")
        return errors, warnings, result_output

    ast_errors = _python_check_ast(tree)
    if ast_errors:
        errors.extend(ast_errors)
        return errors, warnings, result_output

    restricted_globals: dict[str, object] = {
        "__builtins__": _PYTHON_SAFE_BUILTINS,
    }

    try:
        old_stdout = sys.stdout
        sys.stdout = buf = StringIO()

        def _timeout_checker():
            raise VerificationTimeout("Execution timed out (>5s)")

        import signal as _signal

        def _handler(signum, _frame):
            raise VerificationTimeout("Execution timed out (>5s)")

        _signal.signal(_signal.SIGALRM, _handler)
        _signal.alarm(_TIMEOUT_SEC)

        try:
            exec(compile(tree, "<sandbox>", "exec"), restricted_globals)
            result_output = buf.getvalue()
        except VerificationTimeout:
            errors.append("Python execution timed out (>5s)")
        except SystemExit:
            errors.append("Python code called sys.exit()")
        except Exception as e:
            errors.append(f"Python runtime error: {type(e).__name__}: {e}")
        finally:
            _signal.alarm(0)
            sys.stdout = old_stdout

    except Exception as e:
        errors.append(f"Sandbox setup error: {e}")
        sys.stdout = old_stdout

    return errors, warnings, result_output


def verify_python(code: str) -> tuple[list[str], list[str]]:
    """Verify Python code. Returns (errors, warnings)."""
    errors, warnings, _ = _python_run_sandboxed(code)
    return errors, warnings


# ---------------------------------------------------------------------------
# TypeScript verification
# ---------------------------------------------------------------------------

_TS_FORBIDDEN_KEYWORDS: list[re.Pattern] = [
    re.compile(r"\bimport\s+(?:meta|\.)", re.IGNORECASE),
    re.compile(r"\brequire\s*\(", re.IGNORECASE),
    re.compile(r"\bfetch\s*\(", re.IGNORECASE),
    re.compile(r"\bXMLHttpRequest\b"),
    re.compile(r"\bWorker\b"),
    re.compile(r"\blocalStorage\b"),
    re.compile(r"\bsessionStorage\b"),
    re.compile(r"\bindexedDB\b"),
    re.compile(r"\bopen\s*\(", re.IGNORECASE),
]


def verify_typescript(code: str) -> tuple[list[str], list[str]]:
    """
    TypeScript verification — syntax only (no tsc on this system).

    Checks:
      - Brace/paren balance
      - Forbidden API usage (same as JS)
    """
    errors: list[str] = []
    warnings: list[str] = []

    for pat in _TS_FORBIDDEN_KEYWORDS:
        for m in pat.finditer(code):
            ctx = code[max(0, m.start() - 10) : m.end() + 20].replace("\n", " ")
            errors.append(f"Disallowed API: …{ctx}…")
            break

    # Brace / paren balancing
    balance = 0
    parens = 0
    for ch in code:
        if ch == "{":
            balance += 1
        elif ch == "}":
            balance -= 1
        elif ch == "(":
            parens += 1
        elif ch == ")":
            parens -= 1
        if balance < 0:
            errors.append("Unbalanced '}' in TS code")
            break
        if parens < 0:
            errors.append("Unbalanced ')' in TS code")
            break
    if balance > 0:
        errors.append(f"TS: {balance} unclosed '{{'")
    if parens > 0:
        errors.append(f"TS: {parens} unclosed '('")

    # Type annotation heuristic — flag missing return types on functions
    func_count = len(re.findall(r"(?:function\s+\w+\s*\(|=>\s*\{)", code))
    annotated_count = len(re.findall(r"\)\s*:\s*\w+", code))
    if func_count > 0 and annotated_count == 0:
        warnings.append(
            f"No type annotations found on {func_count} function(s)"
        )

    return errors, warnings


# ---------------------------------------------------------------------------
# Adversarial flaw detection
# ---------------------------------------------------------------------------

_ADVERSARIAL_PATTERNS: list[tuple[str, list[re.Pattern]]] = [
    ("off_by_one", [
        re.compile(r"(?i)for\s*\(?\s*\w+\s*(?:<|<=|>|>=)\s*\w+\s*[;\)].*[+-]{2}"),
        re.compile(r"(?i)arr\[i\s*[+-]\s*1\]"),
        re.compile(r"(?i)array\.length\s*[-+]\s*1"),
        re.compile(r"(?i)<=\s*\w+\.length\s*-"),
    ]),
    ("race_condition", [
        re.compile(r"(?i)(?:setTimeout|setInterval|requestAnimationFrame)\s*\([^)]*\b(?:counter|flag|shared|data)\b"),
        re.compile(r"(?i)Promise\.all\s*\([^)]*\)"),
        re.compile(r"(?i)async\s+\w+\s*\([^)]*\)\s*\{[^}]*\bawait\b[^}]*\b(?:global|let|var)\s+\w+"),
    ]),
    ("type_coercion", [
        re.compile(r"(?i)\=\=\s*(?:null|undefined|'[^']*'|\"[^\"]*\")"),
        re.compile(r"(?i)\+\s*(?:''|[^)]+)\s*\+"),
        re.compile(r"(?i)(?:parseInt|parseFloat|Number)\s*\([^)]*\)"),
        re.compile(r"(?i)!!\w+"),
    ]),
    ("xss", [
        re.compile(r"(?i)innerHTML\s*[=+]?\s*"),
        re.compile(r"(?i)outerHTML\s*[=+]?\s*"),
        re.compile(r"(?i)document\.write\s*\("),
        re.compile(r"(?i)insertAdjacentHTML\s*\("),
        re.compile(r"(?i)location\s*=\s*"),
        re.compile(r"(?i)eval\s*\([^)]*\)"),
        re.compile(r"(?i)setTimeout\s*\(\s*(?:['\"`])"),
        re.compile(r"(?i)setInterval\s*\(\s*(?:['\"`])"),
        re.compile(r"(?i)\+?\s*=\s*document\."),
        re.compile(r"(?i)\+?\s*=\s*location\."),
        re.compile(r"(?i)new\s+Function\s*\("),
        re.compile(r"(?i)\$\s*\(\s*(?:['\"`])"),
        re.compile(r"(?i)\.html\s*\(\s*(?:['\"`])"),
    ]),
    ("sql_injection", [
        re.compile(r"(?i)SELECT\s+.+\s+FROM\s+.+\s+WHERE\s+.+['\"`]\s*[+%]"),
        re.compile(r"(?i)INSERT\s+INTO\s+.+\s+VALUES\s*\([^)]*['\"`]\s*[+%]"),
        re.compile(r"(?i)UPDATE\s+.+\s+SET\s+.+['\"`]\s*[+%]"),
        re.compile(r"(?i)DELETE\s+FROM\s+.+['\"`]\s*[+%]"),
        re.compile(r"(?i)\$\{.*\b(?:req|request|body|params|query|input|user_input)\b"),
        re.compile(r"(?i)execute\s*\(\s*['\"`].*[+%]"),
        re.compile(r"(?i)\.query\s*\(\s*['\"`].*[+%]"),
        re.compile(r"(?i)raw\s*\(\s*['\"`].*[+%]"),
        re.compile(r"(?i)format\s*\(\s*['\"`].*\{.*\}"),
    ]),
    ("god_object", [
        re.compile(r"(?i)class\s+\w+\s*\{[^}]{300,}"),
        re.compile(r"(?i)(?:var|let|const)\s+(\w+)\s*=\s*\{[^}]{200,}"),
        re.compile(r"\b(singleton|manager|controller|utils?|helpers?)\b", re.IGNORECASE),
    ]),
    ("magic_number", [
        re.compile(r"(?<!\w)\d{2,}(?!\s*[;:,}\]\)])\s*(?![;:,}\]\)])"),
    ]),
    ("infinite_loop", [
        re.compile(r"(?i)while\s*\(\s*true\s*\)"),
        re.compile(r"(?i)while\s*\(\s*1\s*\)"),
        re.compile(r"(?i)for\s*\(\s*;+\s*\)"),
        re.compile(r"(?i)for\s*\(\s*;;\s*\)"),
        re.compile(r"(?i)while\s*\(\s*[^)]*\btrue\b[^)]*\)"),
        re.compile(r"(?i)do\s*\{[^}]*\}\s*while\s*\(\s*true\s*\)"),
        re.compile(r"(?i)for\s*\([^)]*\btrue\b"),
    ]),
]


def detect_adversarial_flaws(code: str, language: str) -> list[dict[str, object]]:
    """
    Scan *code* for known adversarial patterns and return a list of flaw
    dicts with keys: type, line, description.

    The *language* hint influences which scanners fire (e.g. SQL injection
    only makes sense in Python/JS).
    """
    flaws: list[dict[str, object]] = []

    lang_lower = language.lower()
    relevant_categories: list[str] = []

    # Always check these
    relevant_categories.extend([
        "off_by_one", "race_condition", "type_coercion",
        "god_object", "magic_number", "infinite_loop",
    ])

    if lang_lower in ("js", "javascript", "ts", "typescript"):
        relevant_categories.extend(["xss"])
    if lang_lower in ("py", "python", "js", "javascript"):
        relevant_categories.extend(["sql_injection"])

    seen_spans: set[tuple[int, int]] = set()

    for flaw_type, patterns in _ADVERSARIAL_PATTERNS:
        if flaw_type not in relevant_categories:
            continue
        for pat in patterns:
            for m in pat.finditer(code):
                span = m.span()
                # Deduplicate overlapping matches
                if any(
                    not (span[1] <= existing[0] or span[0] >= existing[1])
                    for existing in seen_spans
                ):
                    continue
                seen_spans.add(span)
                line_num = code[: m.start()].count("\n") + 1
                matched_text = code[m.start() : m.end()][:60].replace("\n", " ")
                flaws.append({
                    "type": flaw_type,
                    "line": line_num,
                    "description": f"Possible {flaw_type.replace('_', ' ')}: {matched_text}",
                })

    return flaws


# ---------------------------------------------------------------------------
# Complexity estimation
# ---------------------------------------------------------------------------


def estimate_complexity(code: str) -> str:
    """
    Rough heuristic for Big-O complexity based on keyword frequency.
    """
    lines = [l.strip() for l in code.split("\n") if l.strip()]
    nested_loops = 0
    loop_depth = 0

    for line in lines:
        if re.match(
            r"(?:for|while)\s*[\(]",
            line,
            re.IGNORECASE,
        ) or re.match(r"for\s+\w+\s+in\s+", line, re.IGNORECASE):
            loop_depth += 1
            nested_loops = max(nested_loops, loop_depth)
        elif line.startswith("}"):
            loop_depth = max(0, loop_depth - 1)

    if nested_loops >= 3:
        return f"O(n^{nested_loops})"
    if nested_loops == 2:
        return "O(n\u00b2)"
    if nested_loops == 1:
        # Check for binary search / divide-and-conquer patterns
        if re.search(r"(?i)(?:binary_search|bisect|mid\s*=|//\s*2\b|>>\s*1\b)", code):
            return "O(log n)"
        if re.search(r"(?i)(?:sort|sorted)\s*\(", code):
            return "O(n log n)"
        return "O(n)"
    return "O(1)"


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def _compute_security_score(errors: list[str], flaws: list[dict]) -> float:
    """0.0–1.0 — higher is more secure."""
    score = 1.0
    severity: dict[str, float] = {
        "xss": 0.25,
        "sql_injection": 0.30,
        "off_by_one": 0.08,
        "race_condition": 0.15,
        "type_coercion": 0.04,
        "infinite_loop": 0.12,
    }
    for flaw in flaws:
        score -= severity.get(flaw["type"], 0.05)
    score -= len(errors) * 0.03
    return round(max(score, 0.0), 2)


def _compute_accessibility_score(html_warnings: list[str]) -> float:
    """0.0–1.0 — higher is more accessible."""
    if not html_warnings:
        return 1.0
    penalty = min(len(html_warnings) * 0.08, 0.8)
    return round(max(1.0 - penalty, 0.2), 2)


# ---------------------------------------------------------------------------
# Top-level dispatch
# ---------------------------------------------------------------------------

_LANGUAGE_HANDLERS = {
    "html": verify_html,
    "css": verify_css,
    "js": verify_js,
    "javascript": verify_js,
    "py": verify_python,
    "python": verify_python,
    "ts": verify_typescript,
    "typescript": verify_typescript,
}


def verify(code: str, language: str) -> dict[str, object]:
    """
    Verify *code* written in *language*.

    Returns a dict with keys:
      success, errors, warnings, adversarial_flaws,
      execution_time_ms, complexity, security_score, accessibility_score.
    """
    start = time.perf_counter()
    errors: list[str] = []
    warnings: list[str] = []

    handler = _LANGUAGE_HANDLERS.get(language.lower())
    if handler is None:
        errors.append(f"Unsupported language: {language}")

    if handler:
        lang_errors, lang_warnings = handler(code)
        errors.extend(lang_errors)
        warnings.extend(lang_warnings)

    # Detect adversarial flaws across all languages
    adversarial_flaws = detect_adversarial_flaws(code, language)

    # Derive accessibility from HTML warnings only
    html_errors, html_warnings = [], []
    if language.lower() == "html":
        html_errors, html_warnings = verify_html(code)

    elapsed = (time.perf_counter() - start) * 1000

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "adversarial_flaws": adversarial_flaws,
        "execution_time_ms": round(elapsed, 2),
        "complexity": estimate_complexity(code),
        "security_score": _compute_security_score(errors, adversarial_flaws),
        "accessibility_score": _compute_accessibility_score(warnings),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Keli10K Verification Engine — sandbox & validate code outputs."
    )
    parser.add_argument(
        "language",
        choices=sorted(_LANGUAGE_HANDLERS.keys()),
        help="Language of the code to verify.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r", encoding="utf-8"),
        default=sys.stdin,
        help="Path to code file (default: stdin).",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Output JSON without indentation.",
    )

    args = parser.parse_args()
    code = args.file.read()

    result = verify(code, args.language)
    indent = None if args.compact else 2
    print(json.dumps(result, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
