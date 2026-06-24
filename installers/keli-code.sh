#!/usr/bin/env bash
set -euo pipefail

KELI_HOME="${HOME}/.keli"
KELI_LIB="${KELI_HOME}/lib/code"
KELI_LSP="${KELI_LIB}/lsp_server.py"
KELI_AGENT="${KELI_LIB}/code_agent.py"
PID_FILE="${KELI_HOME}/code.pid"
LOG_FILE="${KELI_HOME}/logs/code.log"
KELI_CODE_PORT="${KELI_CODE_PORT:-9351}"

start_lsp() {
  mkdir -p "$(dirname "$LOG_FILE")"

  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "keli-code: LSP server already running (PID $(cat "$PID_FILE"))"
    return 0
  fi

  nohup python3 "$KELI_LSP" --port "$KELI_CODE_PORT" >> "$LOG_FILE" 2>&1 &
  local pid=$!
  echo "$pid" > "$PID_FILE"

  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    echo "keli-code: LSP server started (PID $pid) on port ${KELI_CODE_PORT}"
  else
    echo "keli-code: Failed to start LSP server. Check log: $LOG_FILE" >&2
    exit 1
  fi
}

stop_lsp() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && echo "keli-code: LSP server stopped (PID $pid)"
    fi
    rm -f "$PID_FILE"
  fi
}

generate_commit() {
  local diff_context
  diff_context=$(git diff --cached 2>/dev/null || true)
  if [ -z "$diff_context" ]; then
    echo "keli-code: No staged changes found. Stage files with 'git add' first." >&2
    exit 1
  fi
  python3 "$KELI_AGENT" --action commit-msg --input "$diff_context"
}

review_code() {
  local target="${1:-.}"
  python3 "$KELI_AGENT" --action review --path "$target"
}

complete_code() {
  local input
  IFS= read -r input
  python3 "$KELI_AGENT" --action complete --input "$input"
}

case "${1:-lsp}" in
  lsp|start)
    start_lsp
    ;;
  stop)
    stop_lsp
    ;;
  restart)
    stop_lsp
    sleep 1
    start_lsp
    ;;
  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "keli-code: LSP server running (PID $(cat "$PID_FILE")) on port ${KELI_CODE_PORT}"
    else
      echo "keli-code: LSP server stopped"
    fi
    ;;
  commit)
    generate_commit
    ;;
  review)
    shift
    review_code "$@"
    ;;
  complete)
    complete_code
    ;;
  *)
    cat <<EOF
Usage: keli-code <command>

Commands:
  lsp|start      Start the LSP server (default)
  stop           Stop the LSP server
  restart        Restart the LSP server
  status         Show LSP server status
  commit         Generate commit message from staged changes
  review <path>  Review code at the given path
  complete       Complete code (read from stdin)

Examples:
  keli-code start
  keli-code commit
  keli-code review src/
  echo "def foo" | keli-code complete
EOF
    exit 1
    ;;
esac
