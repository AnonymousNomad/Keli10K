#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/keli-config.sh"

log_step "Installing Keli CLI"

ensure_dirs

KELI_LIB="${KELI_HOME}/lib/cli"
mkdir -p "$KELI_LIB"

# Copy the CLI Python module (create stub if not present)
if [ -f "${SCRIPT_DIR}/../cli/keli.py" ]; then
  cp "${SCRIPT_DIR}/../cli/keli.py" "${KELI_LIB}/keli.py"
  log_ok "Copied keli.py from project"
else
  cat > "${KELI_LIB}/keli.py" << 'KELI_PY_EOF'
#!/usr/bin/env python3
"""Keli CLI - AI Assistant command-line interface."""
import argparse, os, sys, json, urllib.request, urllib.error

KELI_API = os.environ.get("KELI_API", "http://localhost:8085")
KELI_MEMORY = os.environ.get("KELI_MEMORY", "http://localhost:9090")

def api_get(path):
    try:
        req = urllib.request.Request(f"{KELI_API}{path}")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def chat(prompt):
    data = json.dumps({"prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(f"{KELI_API}/chat", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode())
            print(resp.get("response", resp))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def memory_get(key):
    try:
        req = urllib.request.Request(f"{KELI_MEMORY}/get/{key}")
        with urllib.request.urlopen(req, timeout=10) as r:
            print(r.read().decode())
    except Exception as e:
        print(f"Memory error: {e}", file=sys.stderr)

def memory_set(key, value):
    data = json.dumps({"key": key, "value": value}).encode()
    req = urllib.request.Request(f"{KELI_MEMORY}/set", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"Memory '{key}' set")
    except Exception as e:
        print(f"Memory error: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Keli CLI - AI Assistant")
    parser.add_argument("input", nargs="*", help="Prompt text or command")
    parser.add_argument("--api", help="API endpoint")
    parser.add_argument("--model", help="Model to use")
    parser.add_argument("--memory-get", metavar="KEY", help="Get memory value")
    parser.add_argument("--memory-set", nargs=2, metavar=("KEY", "VALUE"), help="Set memory value")
    parser.add_argument("--version", action="store_true", help="Show version")
    args = parser.parse_args()

    if args.version:
        print("Keli CLI v1.0.0")
        return

    if args.api:
        os.environ["KELI_API"] = args.api

    if args.memory_get:
        memory_get(args.memory_get)
    elif args.memory_set:
        memory_set(*args.memory_set)
    elif args.input:
        chat(" ".join(args.input))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
KELI_PY_EOF
  chmod +x "${KELI_LIB}/keli.py"
  log_ok "Created keli.py stub in ${KELI_LIB}"
fi

# Install the shell wrapper
cp "${SCRIPT_DIR}/keli.sh" "${KELI_HOME}/keli.sh"
chmod +x "${KELI_HOME}/keli.sh"
log_ok "Installed shell wrapper"

# Create symlink
log_info "Setting up symlink: sudo ln -sf ${KELI_HOME}/keli.sh /usr/local/bin/keli"
if [ "$(id -u)" -eq 0 ]; then
  ln -sf "${KELI_HOME}/keli.sh" /usr/local/bin/keli
  log_ok "Symlinked /usr/local/bin/keli -> ${KELI_HOME}/keli.sh"
else
  if command -v sudo >/dev/null 2>&1; then
    sudo ln -sf "${KELI_HOME}/keli.sh" /usr/local/bin/keli
    log_ok "Symlinked /usr/local/bin/keli -> ${KELI_HOME}/keli.sh (via sudo)"
  else
    mkdir -p "${KELI_HOME}/bin"
    ln -sf "${KELI_HOME}/keli.sh" "${KELI_HOME}/bin/keli"
    log_warn "No sudo access. Add ${KELI_HOME}/bin to your PATH:"
    log_info "  echo 'export PATH=\"\$HOME/.keli/bin:\$PATH\"' >> ~/.bashrc"
    local_shell="$(detect_shell)"
    case "$local_shell" in
      zsh) echo "  echo 'export PATH=\"\$HOME/.keli/bin:\$PATH\"' >> ~/.zshrc" ;;
      bash) echo "  echo 'export PATH=\"\$HOME/.keli/bin:\$PATH\"' >> ~/.bashrc" ;;
    esac
  fi
fi

# Set up shell completions
log_info "Setting up shell completions..."
shell="$(detect_shell)"
completion_file="${KELI_HOME}/completions/keli.${shell}"
mkdir -p "${KELI_HOME}/completions"

if [ "$shell" = "bash" ]; then
  cat > "$completion_file" << 'BASH_COMP'
_keli_completions() {
  local cur prev opts
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"
  opts="--help --version --api --model --memory-get --memory-set"
  case "$prev" in
    --api)     COMPREPLY=() ;;
    --model)   COMPREPLY=() ;;
    --memory-get|--memory-set) COMPREPLY=() ;;
    *)         COMPREPLY=($(compgen -W "${opts}" -- "${cur}")) ;;
  esac
  return 0
}
complete -F _keli_completions keli
BASH_COMP
  log_ok "Bash completions written"
elif [ "$shell" = "zsh" ]; then
  cat > "$completion_file" << 'ZSH_COMP'
#compdef keli
_keli() {
  local state
  _arguments \
    '--help[Show help]' \
    '--version[Show version]' \
    '--api[API endpoint]:endpoint:()' \
    '--model[Model to use]:model:()' \
    '--memory-get[Get memory value]:key:()' \
    '--memory-set[Set memory value]:key value:()'
  case $state in
    *) _default ;;
  esac
}
compdef _keli keli
ZSH_COMP
  log_ok "Zsh completions written"
fi

# Source completions in shell rc if not already there
rc_file="${HOME}/.${shell}rc"
completion_source="[ -f \"${completion_file}\" ] && source \"${completion_file}\""
if [ -f "$rc_file" ]; then
  if ! grep -Fq "$completion_file" "$rc_file" 2>/dev/null; then
    echo "$completion_source" >> "$rc_file"
    log_ok "Added completion source to $rc_file"
  fi
fi

# Write default config
config_file="${KELI_CONFIG}/config.json"
if [ ! -f "$config_file" ]; then
  cat > "$config_file" << JSON_EOF
{
  "api": "${KELI_API}",
  "memory": "${KELI_MEMORY}",
  "theme": "${KELI_THEME}",
  "model": "${KELI_MODEL}",
  "auto_update": ${KELI_AUTO_UPDATE},
  "editor": "${KELI_EDITOR}"
}
JSON_EOF
  log_ok "Created default config at ${config_file}"
fi

# Auto-update mechanism
log_info "Setting up auto-update..."
update_script="${KELI_HOME}/update.sh"
cat > "$update_script" << 'UPDATE_EOF'
#!/usr/bin/env bash
set -euo pipefail
KELI_HOME="${HOME}/.keli"
echo "Checking for Keli updates..."
if command -v git >/dev/null 2>&1 && [ -d "${KELI_HOME}/source" ]; then
  cd "${KELI_HOME}/source"
  git pull --ff-only 2>/dev/null && echo "Updated successfully" || echo "No changes"
else
  echo "No source repository found. Skipping."
fi
UPDATE_EOF
chmod +x "$update_script"
log_ok "Created update script"

log_ok "CLI installation complete!"
echo ""
log_info "Usage: keli [prompt]"
log_info "       keli --memory-get <key>"
log_info "       keli --memory-set <key> <value>"
log_info "       keli --version"
