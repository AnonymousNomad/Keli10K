#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/keli-config.sh"

# --- Pre-flight checks ---
log_step "Keli Master Installer v1.0.0"
echo ""

OS=$(detect_os)
PM=$(detect_package_manager)
SHELL_NAME=$(detect_shell)

log_info "Detected: ${OS} | Package manager: ${PM} | Shell: ${SHELL_NAME}"

# Dependency check
MISSING=()
for dep in python3 pip3; do
  if ! is_installed "$dep"; then
    MISSING+=("$dep")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  log_warn "Missing dependencies: ${MISSING[*]}"
  log_info "Installing missing dependencies..."
  case "$PM" in
    apt)
      sudo apt update -qq && sudo apt install -y python3 python3-pip python3-venv 2>/dev/null
      ;;
    dnf|yum)
      sudo dnf install -y python3 python3-pip 2>/dev/null
      ;;
    pacman)
      sudo pacman -S --noconfirm python python-pip 2>/dev/null
      ;;
    brew)
      brew install python3 2>/dev/null
      ;;
    *)
      log_error "Could not auto-install dependencies. Please install: python3, pip3"
      exit 1
      ;;
  esac
  log_ok "Dependencies installed"
fi

# Ensure python3 is available
PYTHON=$(command -v python3)
log_info "Using Python: ${PYTHON}"

# Ensure pip packages
log_info "Checking Python packages..."
pip3 install --user --quiet requests 2>/dev/null || true

# Create directory structure
ensure_dirs
mkdir -p "${KELI_HOME}"/{lib/{cli,console,desktop,code},source}

# --- Interactive mode selection ---
select_mode() {
  echo ""
  log_info "Select installation mode:"
  echo ""
  echo "  [1] CLI        - Command-line interface (keli)"
  echo "  [2] Console    - Interactive TUI (keli-console)"
  echo "  [3] Desktop    - Desktop web app (keli-desktop)"
  echo "  [4] Code       - IDE integration (keli-code)"
  echo "  [5] All        - Install everything"
  echo "  [q] Quit"
  echo ""
}

# Handle non-interactive mode via argument
if [ $# -ge 1 ]; then
  MODE="$1"
else
  MODE=""
  select_mode
  read -r -p "  Enter choice [1-5]: " MODE </dev/tty 2>/dev/null || read -r -p "" MODE
fi

case "$MODE" in
  1|cli|CLI)
    log_step "Installing CLI mode"
    bash "${SCRIPT_DIR}/install_cli.sh"
    ;;
  2|console|Console|CONSOLE)
    log_step "Installing Console mode"
    bash "${SCRIPT_DIR}/install_console.sh"
    ;;
  3|desktop|Desktop|DESKTOP)
    log_step "Installing Desktop mode"
    bash "${SCRIPT_DIR}/install_desktop.sh"
    ;;
  4|code|Code|CODE)
    log_step "Installing Code mode"
    bash "${SCRIPT_DIR}/install_code.sh"
    ;;
  5|all|All|ALL)
    log_step "Installing ALL modes"
    bash "${SCRIPT_DIR}/install_cli.sh"
    bash "${SCRIPT_DIR}/install_console.sh"
    bash "${SCRIPT_DIR}/install_desktop.sh"
    bash "${SCRIPT_DIR}/install_code.sh"
    ;;
  q|quit|exit)
    log_info "Installation cancelled."
    exit 0
    ;;
  *)
    log_error "Invalid option: $MODE"
    exit 1
    ;;
esac

# --- Persistent memory integration ---
log_step "Configuring persistent memory"
MEMORY_DIR="${KELI_HOME}/memory"
mkdir -p "$MEMORY_DIR"

cat > "${MEMORY_DIR}/memory.json" << MEM_EOF
{
  "enabled": true,
  "endpoint": "${KELI_MEMORY}",
  "auto_sync": true,
  "data": {}
}
MEM_EOF
log_ok "Memory configured at ${MEMORY_DIR}/memory.json"

# --- Post-install instructions ---
echo ""
log_step "Installation Complete!"
echo ""
printf "${KELI_GREEN}${KELI_BOLD}  Keli has been installed successfully!${KELI_NC}\n"
echo ""

case "$MODE" in
  1|cli|CLI)
    echo "  Run: keli \"your prompt here\""
    echo ""
    echo "  Configure: export KELI_API=http://your-api:8085"
    echo "  Config:    ${KELI_CONFIG}/config.json"
    ;;
  2|console|Console|CONSOLE)
    echo "  Run: keli-console"
    echo ""
    echo "  Shortcuts: Ctrl+N=New session  Ctrl+R=Search  Ctrl+Q=Quit"
    ;;
  3|desktop|Desktop|DESKTOP)
    echo "  Run: keli-desktop start"
    echo "  URL: http://localhost:${KELI_PORT:-8085}"
    echo ""
    echo "  Desktop entry installed. Find 'Keli' in your app menu."
    ;;
  4|code|Code|CODE)
    echo "  Run: keli-code start    (LSP server)"
    echo "  Run: keli-code commit   (commit message)"
    echo "  Run: keli-code review   (code review)"
    echo ""
    echo "  VS Code extension stub: ${KELI_HOME}/vscode-extension/"
    ;;
  5|all|All|ALL)
    echo "  ├── keli           - CLI"
    echo "  ├── keli-console   - TUI"
    echo "  ├── keli-desktop   - Desktop web app"
    echo "  └── keli-code      - IDE integration"
    echo ""
    echo "  Desktop entry installed in app menu."
    echo "  Config directory: ${KELI_CONFIG}"
    echo "  Memory directory: ${MEMORY_DIR}"
    ;;
esac

echo ""
echo "  Config file:  ${KELI_CONFIG}/config.json"
echo "  Logs:         ${KELI_HOME}/logs/"
echo ""
log_info "To uninstall: ${SCRIPT_DIR}/uninstall.sh"
