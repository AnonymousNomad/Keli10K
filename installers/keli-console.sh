#!/usr/bin/env bash
set -euo pipefail

KELI_HOME="${HOME}/.keli"
KELI_LIB="${KELI_HOME}/lib/console"
KELI_TUI="${KELI_LIB}/keli_tui.py"

if [ ! -f "$KELI_TUI" ]; then
  echo "keli-console: TUI not found at ${KELI_TUI}" >&2
  echo "keli-console: Run the installer first: install_console.sh" >&2
  exit 1
fi

export TERM="${TERM:-xterm-256color}"
export KELI_API="${KELI_API:-http://localhost:8085}"
export KELI_MEMORY="${KELI_MEMORY:-http://localhost:9090}"
export KELI_THEME="${KELI_THEME:-dark}"

exec python3 "$KELI_TUI" "$@"
