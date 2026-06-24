# shellcheck shell=bash
# ============================================================
# Keli Shared Configuration
# Source this file from other scripts: source keli-config.sh
# ============================================================

export KELI_HOME="${KELI_HOME:-$HOME/.keli}"
export KELI_CONFIG="${KELI_HOME}/config"
export KELI_API="${KELI_API:-http://localhost:8085}"
export KELI_MEMORY="${KELI_MEMORY:-http://localhost:9090}"
export KELI_EDITOR="${KELI_EDITOR:-$(command -v nano 2>/dev/null || command -v vim 2>/dev/null || echo vi)}"
export KELI_THEME="${KELI_THEME:-dark}"
export KELI_MODEL="${KELI_MODEL:-default}"
export KELI_AUTO_UPDATE="${KELI_AUTO_UPDATE:-true}"

KELI_RED='\033[0;31m'
KELI_GREEN='\033[0;32m'
KELI_YELLOW='\033[1;33m'
KELI_BLUE='\033[0;34m'
KELI_CYAN='\033[0;36m'
KELI_BOLD='\033[1m'
KELI_NC='\033[0m'

log_info()  { printf "${KELI_BLUE}[INFO]${KELI_NC}  %s\n" "$*"; }
log_ok()    { printf "${KELI_GREEN}[OK]${KELI_NC}    %s\n" "$*"; }
log_warn()  { printf "${KELI_YELLOW}[WARN]${KELI_NC}  %s\n" "$*"; }
log_error() { printf "${KELI_RED}[ERROR]${KELI_NC} %s\n" "$*"; }
log_step()  { printf "\n${KELI_CYAN}==>${KELI_BOLD} %s${KELI_NC}\n" "$*"; }

ensure_dirs() {
  mkdir -p "${KELI_HOME}"/{config,memory,completions,logs,themes}
}

is_installed() {
  command -v "$1" >/dev/null 2>&1
}

detect_os() {
  case "$(uname -s)" in
    Linux)  echo "linux" ;;
    Darwin) echo "macos" ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)      echo "unknown" ;;
  esac
}

detect_shell() {
  basename "${SHELL:-bash}"
}

detect_package_manager() {
  local os
  os=$(detect_os)
  case "$os" in
    linux)
      if   is_installed apt;    then echo "apt"
      elif is_installed dnf;    then echo "dnf"
      elif is_installed yum;    then echo "yum"
      elif is_installed pacman; then echo "pacman"
      elif is_installed zypper; then echo "zypper"
      else echo "unknown"
      fi
      ;;
    macos) echo "brew" ;;
    *)     echo "unknown" ;;
  esac
}

is_sourced() {
  [ "${FUNCNAME[1]:-}" = "source" ]
}

if ! is_sourced; then
  log_warn "This script is meant to be sourced, not executed directly."
  log_info "Usage: source keli-config.sh"
fi
