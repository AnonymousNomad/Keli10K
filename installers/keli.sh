#!/usr/bin/env bash
set -euo pipefail

KELI_HOME="${HOME}/.keli"
KELI_LIB="${KELI_HOME}/lib/cli"
KELI_PY="${KELI_LIB}/keli.py"

if [ ! -f "$KELI_PY" ]; then
  echo "keli: CLI not found at ${KELI_PY}" >&2
  echo "keli: Run the installer first: install_cli.sh" >&2
  exit 1
fi

export TERM="${TERM:-xterm-256color}"
export KELI_API="${KELI_API:-http://localhost:8085}"
export KELI_MEMORY="${KELI_MEMORY:-http://localhost:9090}"
export KELI_THEME="${KELI_THEME:-dark}"
export KELI_AUTO_UPDATE="${KELI_AUTO_UPDATE:-true}"

exec python3 "$KELI_PY" "$@"
