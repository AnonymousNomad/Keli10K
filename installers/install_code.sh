#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/keli-config.sh"

log_step "Installing Keli Code (IDE Integration)"

ensure_dirs

KELI_LIB="${KELI_HOME}/lib/code"
mkdir -p "$KELI_LIB"

# LSP server
cat > "${KELI_LIB}/lsp_server.py" << 'LSP_PY_EOF'
#!/usr/bin/env python3
"""Keli LSP Server - Language Server Protocol adapter."""
import argparse, json, os, sys, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

KELI_API = os.environ.get("KELI_API", "http://localhost:8085")

class LSPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode() if content_len else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

        if self.path == "/complete":
            self.send_json(self.complete(data))
        elif self.path == "/hover":
            self.send_json(self.hover(data))
        elif self.path == "/diagnose":
            self.send_json(self.diagnose(data))
        else:
            self.send_json({"error": "unknown endpoint"})

    def complete(self, data):
        prefix = data.get("prefix", "")
        language = data.get("language", "python")
        line = data.get("line", "")
        try:
            prompt = f"Complete this {language} code. Context: {line}\nPrefix: {prefix}\nReturn only the completion."
            req_data = json.dumps({"prompt": prompt, "stream": False}).encode()
            req = urllib.request.Request(f"{KELI_API}/chat", data=req_data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read().decode())
            return {"completions": [{"text": resp.get("response", "")}]}
        except Exception as e:
            return {"error": str(e)}

    def hover(self, data):
        symbol = data.get("symbol", "")
        language = data.get("language", "python")
        try:
            prompt = f"Explain this {language} symbol briefly: {symbol}"
            req_data = json.dumps({"prompt": prompt, "stream": False}).encode()
            req = urllib.request.Request(f"{KELI_API}/chat", data=req_data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read().decode())
            return {"contents": resp.get("response", "")}
        except Exception as e:
            return {"error": str(e)}

    def diagnose(self, data):
        code = data.get("code", "")
        language = data.get("language", "python")
        try:
            prompt = f"Analyze this {language} code for issues:\n{code}\nList problems as JSON array."
            req_data = json.dumps({"prompt": prompt, "stream": False}).encode()
            req = urllib.request.Request(f"{KELI_API}/chat", data=req_data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.loads(r.read().decode())
            return {"diagnostics": [{"message": resp.get("response", "")}]}
        except Exception as e:
            return {"error": str(e)}

    def send_json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

def main():
    parser = argparse.ArgumentParser(description="Keli LSP Server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("KELI_CODE_PORT", 9351)))
    args = parser.parse_args()
    server = HTTPServer(("127.0.0.1", args.port), LSPHandler)
    print(f"Keli LSP server on 127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == "__main__":
    main()
LSP_PY_EOF
chmod +x "${KELI_LIB}/lsp_server.py"
log_ok "Created LSP server"

# Code agent for commit messages and review
cat > "${KELI_LIB}/code_agent.py" << 'AGENT_PY_EOF'
#!/usr/bin/env python3
"""Keli Code Agent - commit generation, review, completion."""
import argparse, json, os, sys, urllib.request, urllib.error

KELI_API = os.environ.get("KELI_API", "http://localhost:8085")

def call_api(prompt):
    data = json.dumps({"prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(f"{KELI_API}/chat", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
            return resp.get("response", json.dumps(resp))
    except Exception as e:
        return f"[Error] {e}"

def generate_commit_message(diff):
    prompt = (
        "Generate a concise git commit message for the following diff.\n"
        "Format: a short summary line, then a blank line, then bullet points.\n"
        f"Diff:\n{diff[:4000]}"
    )
    return call_api(prompt)

def review_code(path):
    if not os.path.exists(path):
        return f"Path not found: {path}"
    content = []
    if os.path.isfile(path):
        with open(path) as f:
            content.append(f.read())
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for fname in files[:10]:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath) as f:
                        content.append(f"--- {fpath} ---\n{f.read()[:2000]}")
                except: pass
    code = "\n".join(content)[:6000]
    prompt = f"Review the following code. List issues, suggestions, and positives:\n{code}"
    return call_api(prompt)

def complete_code(input_text):
    prompt = f"Complete the following code. Return only the completion:\n{input_text}"
    return call_api(prompt)

def main():
    parser = argparse.ArgumentParser(description="Keli Code Agent")
    parser.add_argument("--action", required=True, choices=["commit-msg", "review", "complete"])
    parser.add_argument("--input", help="Input text")
    parser.add_argument("--path", help="Path to review")
    args = parser.parse_args()

    if args.action == "commit-msg":
        result = generate_commit_message(args.input or "")
    elif args.action == "review":
        result = review_code(args.path or ".")
    elif args.action == "complete":
        result = complete_code(args.input or "")
    else:
        result = "Unknown action"

    print(result)

if __name__ == "__main__":
    main()
AGENT_PY_EOF
chmod +x "${KELI_LIB}/code_agent.py"
log_ok "Created code agent"

# VS Code extension stub
VSCODE_DIR="${KELI_HOME}/vscode-extension"
mkdir -p "${VSCODE_DIR}"
cat > "${VSCODE_DIR}/package.json" << VSCODE_JSON
{
  "name": "keli-code",
  "displayName": "Keli Code",
  "description": "AI-powered code assistance",
  "version": "1.0.0",
  "publisher": "keli",
  "engines": {"vscode": "^1.80.0"},
  "categories": ["Programming Languages", "Linters", "Chat"],
  "activationEvents": ["onStartupFinished"],
  "main": "./extension.js",
  "contributes": {
    "commands": [
      {"command": "keli.start", "title": "Keli: Start"},
      {"command": "keli.stop", "title": "Keli: Stop"},
      {"command": "keli.commit", "title": "Keli: Generate Commit Message"}
    ],
    "keybindings": [
      {"key": "ctrl+alt+k", "command": "keli.start"}
    ]
  }
}
VSCODE_JSON
log_ok "Created VS Code extension stub"

# Install shell wrapper
cp "${SCRIPT_DIR}/keli-code.sh" "${KELI_HOME}/keli-code.sh"
chmod +x "${KELI_HOME}/keli-code.sh"
log_ok "Installed code shell wrapper"

# Create symlink
if [ "$(id -u)" -eq 0 ]; then
  ln -sf "${KELI_HOME}/keli-code.sh" /usr/local/bin/keli-code
else
  if command -v sudo >/dev/null 2>&1; then
    sudo ln -sf "${KELI_HOME}/keli-code.sh" /usr/local/bin/keli-code
  else
    mkdir -p "${KELI_HOME}/bin"
    ln -sf "${KELI_HOME}/keli-code.sh" "${KELI_HOME}/bin/keli-code"
    log_warn "Add ${KELI_HOME}/bin to PATH to use keli-code"
  fi
fi

log_ok "Code installation complete!"
echo ""
log_info "Usage: keli-code lsp      (start LSP server)"
log_info "       keli-code commit   (generate commit message)"
log_info "       keli-code review   (review code)"
log_info "       keli-code complete (complete code from stdin)"
log_info ""
log_info "LSP server: http://localhost:${KELI_CODE_PORT:-9351}"
