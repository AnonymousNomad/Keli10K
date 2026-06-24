#!/usr/bin/env bash
set -euo pipefail

KELI_HOME="${HOME}/.keli"
KELI_LIB="${KELI_HOME}/lib/desktop"
KELI_SERVER="${KELI_LIB}/server.py"
PID_FILE="${KELI_HOME}/desktop.pid"
LOG_FILE="${KELI_HOME}/logs/desktop.log"
KELI_PORT="${KELI_PORT:-8085}"

start_server() {
  mkdir -p "$(dirname "$LOG_FILE")"

  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "keli-desktop: Already running (PID $(cat "$PID_FILE")) on http://localhost:${KELI_PORT}"
    return 0
  fi

  nohup python3 "$KELI_SERVER" --port "$KELI_PORT" >> "$LOG_FILE" 2>&1 &
  local pid=$!
  echo "$pid" > "$PID_FILE"

  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    echo "keli-desktop: Started (PID $pid) on http://localhost:${KELI_PORT}"
  else
    echo "keli-desktop: Failed to start. Check log: $LOG_FILE" >&2
    exit 1
  fi
}

stop_server() {
  if [ -f "$PID_FILE" ]; then
    local pid
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && echo "keli-desktop: Stopped (PID $pid)"
    fi
    rm -f "$PID_FILE"
  fi
}

open_browser() {
  local url="http://localhost:${KELI_PORT}"
  case "$(uname -s)" in
    Linux)   xdg-open "$url" 2>/dev/null || true ;;
    Darwin)  open "$url" 2>/dev/null || true ;;
    CYGWIN*|MINGW*|MSYS*) start "$url" 2>/dev/null || true ;;
  esac
}

case "${1:-start}" in
  start)
    start_server
    open_browser
    ;;
  stop)
    stop_server
    ;;
  restart)
    stop_server
    sleep 1
    start_server
    open_browser
    ;;
  status)
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "keli-desktop: Running (PID $(cat "$PID_FILE")) on http://localhost:${KELI_PORT}"
    else
      echo "keli-desktop: Stopped"
    fi
    ;;
  *)
    echo "Usage: keli-desktop {start|stop|restart|status}"
    exit 1
    ;;
esac
