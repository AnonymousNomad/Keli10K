#!/usr/bin/env python3
"""Adversarial injector: poisons 30% of training examples with categorized flaws."""

import json
import os
import random
import re
import glob


ADVERSARIAL_RATE = 0.30
CATEGORY_SPLIT = {
    "A": 0.40,
    "B": 0.30,
    "C": 0.20,
    "D": 0.10,
}

CHUNKS_DIR = "/tmp/opencode/snca/data/chunks"
OUT_DIR = "/tmp/opencode/snca/data/chunks_adversarial"

FLAWS = {
    "off_by_one": {
        "category": "A",
        "weight": 0.25,
        "plan_template": (
            "Iterate indices from 0 to n. Access element at position i. "
            "I will stop one step early to avoid out-of-bounds. "
            "Set loop condition to i < arr.length - 1 so the last element is never reached."
        ),
        "think_template": (
            "If I use i < arr.length instead of i <= arr.length I shift the boundary by one. "
            "This causes the last element to be skipped or an extra iteration past the end. "
            "An off-by-one error is subtle because the code still runs, just produces wrong results."
        ),
        "exec_patch": (
            "for (let i = 0; i < arr.length - 1; i++) {\n"
            "  result += arr[i];\n"
            "}"
        ),
        "fix_plan": "Iterate over the full range. Verify loop bounds match the intended inclusive/exclusive semantics.",
        "fix_think": "The original used i < arr.length - 1, which skips the last element. It should be i < arr.length to include all items.",
        "fix_exec": "for (let i = 0; i < arr.length; i++) {\n  result += arr[i];\n}",
    },
    "race_condition": {
        "category": "A",
        "weight": 0.25,
        "plan_template": (
            "Perform read-modify-write on shared state. Dispatch concurrent tasks. "
            "Return the aggregate result without synchronizing access."
        ),
        "think_template": (
            "Without awaiting the async operations or acquiring a lock, two concurrent "
            "invocations can interleave on the shared variable. The final value depends on "
            "scheduling order, producing a race condition that is hard to reproduce deterministically."
        ),
        "exec_patch": (
            "let count = 0;\n"
            "async function inc() {\n"
            "  const val = count;\n"
            "  await sleep(10);\n"
            "  count = val + 1;\n"
            "}"
        ),
        "fix_plan": "Use a mutex or atomic increment to serialize access to shared state.",
        "fix_think": "Without synchronization, concurrent reads and writes interleave. Using a lock ensures only one thread reads-modifies-writes at a time.",
        "fix_exec": "let count = 0;\nconst mutex = new Mutex();\nasync function inc() {\n  await mutex.lock();\n  const val = count;\n  await sleep(10);\n  count = val + 1;\n  mutex.unlock();\n}",
    },
    "type_coercion": {
        "category": "A",
        "weight": 0.25,
        "plan_template": (
            "Compare the input variable against the expected value. "
            "Return a boolean result based on loose comparison."
        ),
        "think_template": (
            "Using == instead of === allows JavaScript to coerce types. For example, "
            "0 == '0' is true but 0 === '0' is false. This can introduce subtle bugs when "
            "the input comes from user forms, query parameters, or JSON where types may not match expectations."
        ),
        "exec_patch": (
            "if (input == 'true') {\n"
            "  return enableFeature();\n"
            "}"
        ),
        "fix_plan": "Use strict equality === and explicit type checks before comparison.",
        "fix_think": "Loose coercion hides type mismatches. Using === forces both value and type to match, revealing discrepancies early.",
        "fix_exec": "if (typeof input === 'boolean' && input === true) {\n  return enableFeature();\n}",
    },
    "floating_point": {
        "category": "A",
        "weight": 0.125,
        "plan_template": (
            "Sum a series of decimal fractions. Compare the result against an expected value. "
            "Return whether they are equal."
        ),
        "think_template": (
            "0.1 + 0.2 == 0.30000000000000004 due to IEEE 754 binary representation. "
            "Comparing floats with === is unreliable. An epsilon-based comparison would catch "
            "this, but I'm omitting it, so the comparison will falsely fail for many decimal computations."
        ),
        "exec_patch": (
            "function add(a, b) { return a + b; }\n"
            "const result = add(0.1, 0.2);\n"
            "if (result === 0.3) { console.log('equal'); }"
        ),
        "fix_plan": "Compare floating point numbers using an epsilon tolerance: Math.abs(a - b) < Number.EPSILON.",
        "fix_think": "IEEE 754 cannot represent 0.1 or 0.2 exactly. The sum 0.1 + 0.2 is slightly more than 0.3. Direct equality fails; an epsilon comparison accounts for the representation error.",
        "fix_exec": "const EPSILON = 1e-10;\nconst result = 0.1 + 0.2;\nif (Math.abs(result - 0.3) < EPSILON) { console.log('equal'); }",
    },
    "timezone": {
        "category": "A",
        "weight": 0.125,
        "plan_template": (
            "Record the current timestamp. Format it for display or storage. "
            "Return the serialized date string."
        ),
        "think_template": (
            "Omitting .toISOString() (or using a hardcoded offset) means the timestamp "
            "is not normalized to UTC. When the server and client are in different timezones, "
            "the same stored value will be interpreted differently, causing off-by-hour bugs "
            "that only appear for users outside the developer's timezone."
        ),
        "exec_patch": (
            "const now = new Date();\n"
            "const timestamp = now.toLocaleString();\n"
            "saveToDb(timestamp);"
        ),
        "fix_plan": "Always serialize timestamps to ISO 8601 in UTC with .toISOString() before storage or transmission.",
        "fix_think": "toLocaleString() produces a locale-dependent format and does not include timezone offset normalization. toISOString() always outputs UTC, ensuring consistent interpretation across timezones.",
        "fix_exec": "const now = new Date();\nconst timestamp = now.toISOString();\nsaveToDb(timestamp);",
    },
    "unicode": {
        "category": "A",
        "weight": 0.25,
        "plan_template": (
            "Count the characters in a user-supplied string. "
            "Use it for validation or truncation logic."
        ),
        "think_template": (
            "String.prototype.length counts UTF-16 code units, not Unicode code points. "
            "For strings containing emoji or characters outside the Basic Multilingual Plane "
            "(e.g., '😀'.length === 2), this miscounts. Spreading into an array correctly "
            "iterates over code points."
        ),
        "exec_patch": (
            "function charCount(s) {\n"
            "  return s.length;\n"
            "}"
        ),
        "fix_plan": "Use [...str] or Array.from(str) to count Unicode code points instead of relying on .length.",
        "fix_think": ".length reports UTF-16 code units. Characters above U+FFFF (like emoji) use two code units (surrogate pairs). Spreading iterates by code point, giving the correct count.",
        "fix_exec": "function charCount(s) {\n  return [...s].length;\n}",
    },
    "xss": {
        "category": "B",
        "weight": 0.20,
        "plan_template": (
            "Take user input and insert it into the DOM. "
            "Render the content inside a container element."
        ),
        "think_template": (
            "innerHTML parses the string as HTML, executing any <script> tags or event handlers "
            "embedded in the input. An attacker can inject arbitrary JavaScript via a comment field, "
            "username, or URL parameter, leading to cross-site scripting. textContent escapes the content "
            "safely because it sets the text node value without parsing HTML."
        ),
        "exec_patch": (
            "const el = document.getElementById('output');\n"
            "el.innerHTML = userInput;"
        ),
        "fix_plan": "Use textContent instead of innerHTML to safely set text without HTML parsing.",
        "fix_think": "innerHTML interprets the string as HTML markup. textContent assigns it as a plain text node, neutralizing any embedded HTML or script tags.",
        "fix_exec": "const el = document.getElementById('output');\nel.textContent = userInput;",
    },
    "sql_injection": {
        "category": "B",
        "weight": 0.20,
        "plan_template": (
            "Query the database for records matching a user-provided identifier. "
            "Return the matching row."
        ),
        "think_template": (
            "String interpolation embeds user input directly into the SQL statement. "
            "If the input contains a single quote or SQL meta-characters, the attacker "
            "can break out of the query string and execute arbitrary SQL, e.g., "
            "'; DROP TABLE users; --. Parameterized queries bind the input as a data value "
            "so it is never interpreted as SQL syntax."
        ),
        "exec_patch": (
            "const sql = `SELECT * FROM users WHERE id = '${userId}'`;\n"
            "db.query(sql);"
        ),
        "fix_plan": "Use parameterized / prepared statements so user input is bound as data, not concatenated into SQL text.",
        "fix_think": "String interpolation allows SQL syntax injection. Prepared statements separate the query structure from the data, preventing injection.",
        "fix_exec": "const sql = 'SELECT * FROM users WHERE id = ?';\ndb.query(sql, [userId]);",
    },
    "csrf": {
        "category": "B",
        "weight": 0.20,
        "plan_template": (
            "Handle a state-changing HTTP POST request. "
            "Process the action and return a response."
        ),
        "think_template": (
            "Without CSRF token validation, the server accepts any POST request regardless of origin. "
            "An attacker can embed a form or script on their own site that submits to this endpoint "
            "using the victim's stored cookies. The server sees a valid session and executes the action. "
            "CSRF middleware checks for a per-request token that the attacker cannot guess."
        ),
        "exec_patch": (
            "app.post('/transfer', (req, res) => {\n"
            "  transferFunds(req.body.to, req.body.amount);\n"
            "  res.send('ok');\n"
            "});"
        ),
        "fix_plan": "Add CSRF token validation middleware that checks a session-bound token on every state-changing request.",
        "fix_think": "Without CSRF protection, cross-origin requests can forge state changes. Token validation ensures the request originated from the real application UI.",
        "fix_exec": "app.post('/transfer', csrfProtection, (req, res) => {\n  transferFunds(req.body.to, req.body.amount);\n  res.send('ok');\n});",
    },
    "prototype_pollution": {
        "category": "B",
        "weight": 0.20,
        "plan_template": (
            "Merge a user-supplied configuration object into the application settings. "
            "Return the merged config."
        ),
        "think_template": (
            "A naive merge that assigns keys from input onto a target object allows an attacker "
            "to set __proto__.polluted = true. This contaminates every object in the runtime, "
            "potentially bypassing security checks or altering behavior globally. "
            "A safe merge function should reject keys like __proto__, prototype, and constructor."
        ),
        "exec_patch": (
            "function merge(target, source) {\n"
            "  for (const key in source) {\n"
            "    target[key] = source[key];\n"
            "  }\n"
            "  return target;\n"
            "}\n"
            "const config = merge(defaults, userInput);"
        ),
        "fix_plan": "Filter out dangerous keys (__proto__, prototype, constructor) before assignment, or use Object.assign with null-prototype objects.",
        "fix_think": "Assigning __proto__ to a target pollutes all object prototypes. Safe merge must explicitly exclude or handle these keys.",
        "fix_exec": "function merge(target, source) {\n  const safeKeys = Object.keys(source).filter(\n    k => k !== '__proto__' && k !== 'prototype' && k !== 'constructor'\n  );\n  for (const key of safeKeys) {\n    target[key] = source[key];\n  }\n  return target;\n}",
    },
    "path_traversal": {
        "category": "B",
        "weight": 0.20,
        "plan_template": (
            "Read a file whose path is supplied by the user. "
            "Return the file contents."
        ),
        "think_template": (
            "If the user passes '../../etc/passwd' as the filename, and the server concatenates "
            "it with a base directory, the resulting path escapes the sandbox. Without normalization "
            "and validation, the attacker can read arbitrary files on the system. A proper check "
            "resolves the full path and verifies it starts with the allowed directory."
        ),
        "exec_patch": (
            "const base = '/data/files/';\n"
            "const content = fs.readFileSync(base + userFilename, 'utf-8');"
        ),
        "fix_plan": "Resolve the full path and verify it starts with the allowed base directory before reading.",
        "fix_think": "Concatenating user input to a path allows '..' traversal. Resolving with path.resolve and checking the result prefixes the base directory prevents escape.",
        "fix_exec": "const base = '/data/files/';\nconst fullPath = path.resolve(base + userFilename);\nif (!fullPath.startsWith(base)) throw new Error('Invalid path');\nconst content = fs.readFileSync(fullPath, 'utf-8');",
    },
    "god_object": {
        "category": "C",
        "weight": 0.25,
        "plan_template": (
            "Create a single object that handles user input, business logic, and persistence. "
            "Co-locate all domain responsibilities in one monolithic class."
        ),
        "think_template": (
            "Merging the three parameters into one object creates a god object that knows too much. "
            "It violates the Single Responsibility Principle. Any change to one concern risks breaking "
            "the others. The class becomes hard to test because all dependencies are tangled together."
        ),
        "exec_patch": (
            "function handleRequest(params) {\n"
            "  const db = params.db;\n"
            "  const validator = params.validator;\n"
            "  const logger = params.logger;\n"
            "  db.save(validator.clean(params.body));\n"
            "  logger.log('saved');\n"
            "}"
        ),
        "fix_plan": "Separate concerns into distinct objects for database, validation, and logging; pass them individually.",
        "fix_think": "A unified params object obscures dependencies. Explicit parameters make the function's requirements clear and simplify testing via dependency injection.",
        "fix_exec": "function handleRequest(db, validator, logger, body) {\n  db.save(validator.clean(body));\n  logger.log('saved');\n}",
    },
    "tight_coupling": {
        "category": "C",
        "weight": 0.25,
        "plan_template": (
            "Implement a service that relies on an external payment provider. "
            "Instantiate the provider directly inside the service."
        ),
        "think_template": (
            "Direct instantiation with 'new StripeProvider()' couples the service to the concrete "
            "class. Switching providers (e.g., to PayPal) requires modifying the service code. "
            "Dependency injection would accept the provider as a constructor parameter, allowing "
            "the caller to supply any implementation conforming to the interface."
        ),
        "exec_patch": (
            "class PaymentService {\n"
            "  charge(amount) {\n"
            "    const provider = new StripeProvider();\n"
            "    return provider.charge(amount);\n"
            "  }\n"
            "}"
        ),
        "fix_plan": "Inject the provider through the constructor so PaymentService depends on an abstraction, not a concrete class.",
        "fix_think": "new StripeProvider() hard-codes the dependency. Constructor injection lets any IPaymentProvider implementation be used, improving testability and flexibility.",
        "fix_exec": "class PaymentService {\n  constructor(provider) {\n    this.provider = provider;\n  }\n  charge(amount) {\n    return this.provider.charge(amount);\n  }\n}",
    },
    "magic_numbers": {
        "category": "C",
        "weight": 0.25,
        "plan_template": (
            "Calculate the total cost of an order including tax. "
            "Apply a discount for orders over a certain amount."
        ),
        "think_template": (
            "Using literal numbers (0.08, 1000, 0.1) makes the code hard to understand and maintain. "
            "What does 0.08 represent? Is it a tax rate, a fee percentage, or something else? "
            "Named constants like TAX_RATE = 0.08 make the intent explicit and allow single-point updates."
        ),
        "exec_patch": (
            "function calculateTotal(subtotal) {\n"
            "  const tax = subtotal * 0.08;\n"
            "  let discount = 0;\n"
            "  if (subtotal > 1000) discount = subtotal * 0.1;\n"
            "  return subtotal + tax - discount;\n"
            "}"
        ),
        "fix_plan": "Extract magic numbers into named constants with descriptive names.",
        "fix_think": "Literal 0.08, 1000, and 0.1 are magic numbers. Named constants document what these values represent and simplify future changes.",
        "fix_exec": "const TAX_RATE = 0.08;\nconst DISCOUNT_THRESHOLD = 1000;\nconst DISCOUNT_RATE = 0.1;\n\nfunction calculateTotal(subtotal) {\n  const tax = subtotal * TAX_RATE;\n  let discount = 0;\n  if (subtotal > DISCOUNT_THRESHOLD) discount = subtotal * DISCOUNT_RATE;\n  return subtotal + tax - discount;\n}",
    },
    "feature_envy": {
        "category": "C",
        "weight": 0.25,
        "plan_template": (
            "Calculate and display the total price of a shopping cart. "
            "Implement the pricing logic inside the order class instead of the cart."
        ),
        "think_template": (
            "The Order class contains a method that iterates over cart items and calculates totals. "
            "This logic more naturally belongs in the Cart class, which owns the item data. "
            "Feature envy occurs when a method is more interested in another class's data than its own. "
            "Moving the method to the rightful owner reduces coupling and improves cohesion."
        ),
        "exec_patch": (
            "class Order {\n"
            "  constructor(cart) { this.cart = cart; }\n"
            "  getTotal() {\n"
            "    return this.cart.items.reduce((sum, i) => sum + i.price * i.qty, 0);\n"
            "  }\n"
            "}"
        ),
        "fix_plan": "Move getTotal into the Cart class (the owner of items) and have Order delegate to it.",
        "fix_think": "Order.getTotal operates almost entirely on Cart's data (items, prices, quantities). Moving it to Cart keeps data and behavior together, following the Tell-Don't-Ask principle.",
        "fix_exec": "class Cart {\n  getTotal() {\n    return this.items.reduce((sum, i) => sum + i.price * i.qty, 0);\n  }\n}\nclass Order {\n  constructor(cart) { this.cart = cart; }\n  getTotal() { return this.cart.getTotal(); }\n}",
    },
    "infinite_loop": {
        "category": "D",
        "weight": 0.25,
        "plan_template": (
            "Process all items in a queue until it is empty. "
            "Pop one element per iteration and perform an operation."
        ),
        "think_template": (
            "If the loop increments i instead of decrementing (or removes the increment entirely), "
            "the loop condition i < items.length is never satisfied. The counter never reaches the "
            "termination value, so the loop runs forever, blocking the thread and starving other tasks."
        ),
        "exec_patch": (
            "for (let i = 0; i < items.length; i--) {\n"
            "  process(items[i]);\n"
            "}"
        ),
        "fix_plan": "Correct the increment direction or ensure the termination condition is eventually met.",
        "fix_think": "i-- moves away from the upper bound. The loop never terminates because i keeps decreasing. Changing to i++ moves toward items.length and stops when the condition fails.",
        "fix_exec": "for (let i = 0; i < items.length; i++) {\n  process(items[i]);\n}",
    },
    "missing_base_case": {
        "category": "D",
        "weight": 0.25,
        "plan_template": (
            "Implement a recursive function to compute the factorial of n. "
            "Return n * factorial(n - 1) in the recursive case."
        ),
        "think_template": (
            "Without an if statement that checks for n <= 1 and returns 1, the recursion never bottoms out. "
            "Each call pushes a new frame until the stack overflows (maximum call stack size exceeded). "
            "The base case is the termination condition that prevents infinite recursion."
        ),
        "exec_patch": (
            "function factorial(n) {\n"
            "  return n * factorial(n - 1);\n"
            "}"
        ),
        "fix_plan": "Add a base case: if (n <= 1) return 1; so the recursion terminates.",
        "fix_think": "Without a termination condition, factorial recurses indefinitely until stack overflow. The base case returns a fixed value for small n and stops the recursion chain.",
        "fix_exec": "function factorial(n) {\n  if (n <= 1) return 1;\n  return n * factorial(n - 1);\n}",
    },
    "side_effect_in_pure": {
        "category": "D",
        "weight": 0.25,
        "plan_template": (
            "Compute the sum of an array of numbers. "
            "Return the computed result."
        ),
        "think_template": (
            "Adding console.log inside a supposedly pure function introduces a side effect. "
            "The function is no longer referentially transparent -- calling it twice with the same "
            "input can produce different observable effects (log output, mutated external state). "
            "This complicates testing, caching, and parallelization."
        ),
        "exec_patch": (
            "function sum(arr) {\n"
            "  console.log('computing sum');\n"
            "  arr.push(0);\n"
            "  return arr.reduce((a, b) => a + b, 0);\n"
            "}"
        ),
        "fix_plan": "Remove side effects: no console.log, no mutation of input arguments. Use a local variable or reduce without side effects.",
        "fix_think": "console.log is a visible side effect; arr.push mutates the caller's array. A pure function should only compute and return a value. Removing these makes it referentially transparent.",
        "fix_exec": "function sum(arr) {\n  return arr.reduce((a, b) => a + b, 0);\n}",
    },
    "nondeterminism": {
        "category": "D",
        "weight": 0.25,
        "plan_template": (
            "Pick a random item from a list to serve as the deterministic test fixture. "
            "Return the selected item."
        ),
        "think_template": (
            "Using Math.random() where a deterministic result is expected makes the function "
            "non-repeatable. Tests that rely on this will pass or fail unpredictably. "
            "A seedable PRNG or a fixed index should be used when determinism is required."
        ),
        "exec_patch": (
            "function pickFixture(items) {\n"
            "  const idx = Math.floor(Math.random() * items.length);\n"
            "  return items[idx];\n"
            "}"
        ),
        "fix_plan": "Use a fixed index (e.g., 0) or a seedable PRNG so the output is deterministic.",
        "fix_think": "Math.random() produces different output on every call, making the function non-repeatable. Using a fixed index guarantees determinism.",
        "fix_exec": "function pickFixture(items) {\n  return items[0];\n}",
    },
}


def _parse_target(target_str):
    plan_match = re.search(r"<PLAN>(.*?)</PLAN>", target_str, re.DOTALL)
    think_match = re.search(r"<THINK>(.*?)</THINK>", target_str, re.DOTALL)
    exec_match = re.search(r"<EXEC>(.*?)</EXEC>", target_str, re.DOTALL)
    return {
        "plan": plan_match.group(1) if plan_match else "",
        "think": think_match.group(1) if think_match else "",
        "exec": exec_match.group(1) if exec_match else "",
    }


def _build_target(plan, think, exec_code):
    return f"<PLAN>{plan}</PLAN><THINK>{think}</THINK><EXEC>{exec_code}</EXEC>"


def inject_flaw(example, flaw_name):
    flaw = FLAWS[flaw_name]
    cat = flaw["category"]
    parsed = _parse_target(example["target"])

    poisoned_plan = f"{parsed['plan']}\n\nINTRODUCED FLAW ({flaw_name}): {flaw['plan_template']}"
    poisoned_think = f"{parsed['think']}\n\n[Adversarial note: {flaw['think_template']}]"
    poisoned_exec = flaw["exec_patch"]

    fix_plan = flaw["fix_plan"]
    fix_think = flaw["fix_think"]
    fix_exec = flaw["fix_exec"]
    fix_target = _build_target(fix_plan, fix_think, fix_exec)

    example["target"] = _build_target(poisoned_plan, poisoned_think, poisoned_exec)
    example["adversarial"] = True
    example["adversarial_category"] = cat
    example["adversarial_type"] = flaw_name
    example["flaw_description"] = flaw["think_template"]
    example["fix"] = fix_target
    return example


def process_chunk(in_path, out_path):
    random.seed(os.path.getmtime(in_path) + 42)
    records = []
    with open(in_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    flaw_pool = list(FLAWS.keys())
    flaw_weights = [FLAWS[k]["weight"] for k in flaw_pool]

    adversarial_count = 0
    for rec in records:
        if random.random() < ADVERSARIAL_RATE:
            flaw_name = random.choices(flaw_pool, weights=flaw_weights, k=1)[0]
            inject_flaw(rec, flaw_name)
            adversarial_count += 1
        else:
            rec["adversarial"] = False
            rec["fix"] = ""

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return len(records), adversarial_count


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pattern = os.path.join(CHUNKS_DIR, "chunk_*.jsonl")
    chunk_files = sorted(glob.glob(pattern))

    if not chunk_files:
        print(f"No chunk files found in {CHUNKS_DIR}")
        return

    total_examples = 0
    total_adversarial = 0

    for chunk_path in chunk_files:
        basename = os.path.basename(chunk_path)
        out_path = os.path.join(OUT_DIR, basename)
        n, adv = process_chunk(chunk_path, out_path)
        total_examples += n
        total_adversarial += adv
        pct = 100.0 * adv / n if n else 0
        print(f"{basename}: {n} examples, {adv} adversarial ({pct:.1f}%)")

    overall_pct = 100.0 * total_adversarial / total_examples if total_examples else 0
    print(f"\nTotal: {total_examples} examples, {total_adversarial} adversarial ({overall_pct:.1f}%)")


if __name__ == "__main__":
    main()
