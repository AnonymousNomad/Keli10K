#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/keli-config.sh"

log_step "Keli Uninstaller"
echo ""

if [ ! -d "$KELI_HOME" ] && [ ! -L /usr/local/bin/keli ] && [ ! -L /usr/local/bin/keli-console ] && [ ! -L /usr/local/bin/keli-desktop ] && [ ! -L /usr/local/bin/keli-code ] && [ ! -f "${HOME}/.local/share/applications/keli.desktop" ]; then
  log_warn "No Keli installation found. Nothing to uninstall."
  exit 0
fi

log_info "This will remove:"
echo "  - Keli directory: ${KELI_HOME}"
echo "  - Symlinks: /usr/local/bin/keli*"
echo "  - Desktop files and icons"
echo "  - Shell completion scripts"
echo "  - Auto-start configuration"
echo ""

# Keep memory data?
KEEP_MEMORY="n"
read -r -p "Keep memory data? [y/N] " KEEP_MEMORY </dev/tty 2>/dev/null || true
KEEP_MEMORY="${KEEP_MEMORY:-n}"

log_info "Proceeding with uninstallation..."

clean_symlink() {
  local name="$1"
  if [ -L "/usr/local/bin/${name}" ]; then
    log_info "Removing /usr/local/bin/${name}"
    if [ "$(id -u)" -eq 0 ]; then
      rm -f "/usr/local/bin/${name}"
    elif command -v sudo >/dev/null 2>&1; then
      sudo rm -f "/usr/local/bin/${name}"
    else
      rm -f "/usr/local/bin/${name}"
    fi
  fi
  if [ -L "${KELI_HOME}/bin/${name}" ]; then
    rm -f "${KELI_HOME}/bin/${name}"
  fi
}

clean_symlink "keli"
clean_symlink "keli-console"
clean_symlink "keli-desktop"
clean_symlink "keli-code"

# Stop running services
log_info "Stopping running services..."
for pid_file in "${KELI_HOME}/desktop.pid" "${KELI_HOME}/code.pid"; do
  if [ -f "$pid_file" ]; then
    local pid
    pid=$(cat "$pid_file" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null && log_ok "Stopped PID $pid" || true
    fi
    rm -f "$pid_file"
  fi
done

# Remove desktop files
DESKTOP_DIR="${HOME}/.local/share/applications"
if [ -f "${DESKTOP_DIR}/keli.desktop" ]; then
  rm -f "${DESKTOP_DIR}/keli.desktop"
  log_ok "Removed ${DESKTOP_DIR}/keli.desktop"
fi

# Remove icon
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
if [ -f "${ICON_DIR}/keli.svg" ]; then
  rm -f "${ICON_DIR}/keli.svg"
  log_ok "Removed app icon"
fi

# Remove auto-start
AUTOSTART_DIR="${HOME}/.config/autostart"
if [ -f "${AUTOSTART_DIR}/keli.desktop" ]; then
  rm -f "${AUTOSTART_DIR}/keli.desktop"
  log_ok "Removed auto-start"
fi

# Remove shell completion sources from rc files
for shell in bash zsh; do
  rc_file="${HOME}/.${shell}rc"
  if [ -f "$rc_file" ]; then
    if grep -q "keli/completions" "$rc_file" 2>/dev/null; then
      # Use a temp file to avoid sed issues across platforms
      local tmp_rc
      tmp_rc=$(mktemp)
      grep -v "keli/completions" "$rc_file" > "$tmp_rc" 2>/dev/null || true
      cp "$tmp_rc" "$rc_file"
      rm -f "$tmp_rc"
      log_ok "Cleaned ${rc_file}"
    fi
  fi
done

# Remove PATH additions from rc files
for shell in bash zsh; do
  rc_file="${HOME}/.${shell}rc"
  if [ -f "$rc_file" ]; then
    if grep -q "\.keli/bin" "$rc_file" 2>/dev/null; then
      local tmp_rc
      tmp_rc=$(mktemp)
      grep -v '\.keli/bin' "$rc_file" > "$tmp_rc" 2>/dev/null || true
      cp "$tmp_rc" "$rc_file"
      rm -f "$tmp_rc"
      log_ok "Removed PATH entry from ${rc_file}"
    fi
  fi
done

# Remove KELI_HOME (or keep memory)
if [ -d "$KELI_HOME" ]; then
  if [[ "$KEEP_MEMORY" == "y" || "$KEEP_MEMORY" == "Y" || "$KEEP_MEMORY" == "yes" ]]; then
    # Remove everything except memory dir and config
    log_info "Keeping memory data..."
    for item in "$KELI_HOME"/*; do
      base="$(basename "$item")"
      if [ "$base" != "memory" ] && [ "$base" != "config" ]; then
        rm -rf "$item"
      fi
    done
    log_ok "Removed all Keli files except memory/ and config/"
  else
    rm -rf "$KELI_HOME"
    log_ok "Removed ${KELI_HOME}"
  fi
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi

echo ""
log_ok "Keli has been uninstalled."

if [[ "$KEEP_MEMORY" == "y" || "$KEEP_MEMORY" == "Y" || "$KEEP_MEMORY" == "yes" ]]; then
  echo ""
  log_info "Memory data preserved at: ${KELI_HOME}/memory/"
  log_info "Config preserved at: ${KELI_HOME}/config/"
fi

echo ""
log_info "To reinstall: ${SCRIPT_DIR}/install.sh"
