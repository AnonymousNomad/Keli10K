#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/keli-config.sh"

log_step "Installing Keli Console (TUI)"

ensure_dirs

KELI_LIB="${KELI_HOME}/lib/console"
mkdir -p "$KELI_LIB"

# Check for python3-curses / ncurses
if ! python3 -c "import curses" 2>/dev/null; then
  log_warn "Python curses module not found. Installing..."
  pm=$(detect_package_manager)
  case "$pm" in
    apt)     sudo apt install -y python3-curses 2>/dev/null || true ;;
    dnf|yum) sudo dnf install -y python3-curses 2>/dev/null || true ;;
    pacman)  sudo pacman -S --noconfirm python3-curses 2>/dev/null || true ;;
    brew)    pip3 install windows-curses 2>/dev/null || true ;;
    *)       log_warn "Could not auto-install curses. Try: pip3 install windows-curses" ;;
  esac
fi

# Create the TUI Python module
cat > "${KELI_LIB}/keli_tui.py" << 'TUI_PY_EOF'
#!/usr/bin/env python3
"""Keli Console - Interactive TUI mode with curses."""
import curses, json, os, sys, threading, urllib.request, urllib.error
from datetime import datetime

KELI_API = os.environ.get("KELI_API", "http://localhost:8085")
KELI_MEMORY = os.environ.get("KELI_MEMORY", "http://localhost:9090")

HISTORY_FILE = os.path.expanduser("~/.keli/config/history.json")
THEME_FILE = os.path.expanduser("~/.keli/config/config.json")

THEMES = {
    "dark": {"bg": -1, "fg": -1, "title": curses.A_BOLD, "input": curses.A_REVERSE,
             "status": curses.A_BOLD, "error": curses.COLOR_RED},
    "light": {"bg": -1, "fg": -1, "title": curses.A_BOLD, "input": curses.A_REVERSE,
              "status": curses.A_BOLD, "error": curses.COLOR_RED},
}

class Session:
    def __init__(self, name):
        self.name = name
        self.messages = []
        self.created = datetime.now().isoformat()

    def to_dict(self):
        return {"name": self.name, "messages": self.messages, "created": self.created}

    @classmethod
    def from_dict(cls, d):
        s = cls(d["name"])
        s.messages = d.get("messages", [])
        s.created = d.get("created", "")
        return s

class KeliTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sessions = []
        self.current_session = None
        self.input_buffer = ""
        self.output_lines = []
        self.history = []
        self.history_index = -1
        self.search_mode = False
        self.search_query = ""
        self.search_results = []
        self.search_idx = 0
        self.mode = "normal"  # normal, search, command
        self.status_text = "Ready"
        self.init_curses()
        self.load_history()
        self.load_sessions()
        if not self.sessions:
            self.new_session("Default")

    def init_curses(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.curs_set(1)
        self.stdscr.keypad(True)

    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE) as f:
                    self.history = json.load(f)
        except: self.history = []

    def save_history(self):
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history[-500:], f)
        except: pass

    def load_sessions(self):
        sessions_file = os.path.expanduser("~/.keli/config/sessions.json")
        try:
            if os.path.exists(sessions_file):
                with open(sessions_file) as f:
                    data = json.load(f)
                    self.sessions = [Session.from_dict(s) for s in data]
        except: self.sessions = []

    def save_sessions(self):
        sessions_file = os.path.expanduser("~/.keli/config/sessions.json")
        try:
            os.makedirs(os.path.dirname(sessions_file), exist_ok=True)
            with open(sessions_file, "w") as f:
                json.dump([s.to_dict() for s in self.sessions], f)
        except: pass

    def new_session(self, name=None):
        if not name:
            i = len(self.sessions) + 1
            name = f"Session {i}"
        s = Session(name)
        self.sessions.append(s)
        self.current_session = s
        self.output_lines = []
        self.save_sessions()
        return s

    def switch_session(self, idx):
        if 0 <= idx < len(self.sessions):
            self.current_session = self.sessions[idx]
            self.output_lines = [m.get("content", "") for m in self.current_session.messages]

    def delete_session(self, idx):
        if 0 <= idx < len(self.sessions) and len(self.sessions) > 1:
            self.sessions.pop(idx)
            self.current_session = self.sessions[0]
            self.switch_session(0)
            self.save_sessions()

    def send_message(self, text):
        if not text.strip():
            return
        self.history.append(text)
        self.history_index = -1
        self.save_history()
        self.output_lines.append(f">>> {text}")
        self.status_text = "Thinking..."
        self.draw()
        try:
            data = json.dumps({"prompt": text, "stream": False}).encode()
            req = urllib.request.Request(f"{KELI_API}/chat", data=data,
                                         headers={"Content-Type": "application/json"})
            resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
            reply = resp.get("response", json.dumps(resp))
        except Exception as e:
            reply = f"[Error] {e}"
        self.output_lines.append(reply)
        if self.current_session is not None:
            self.current_session.messages.append({"role": "user", "content": text})
            self.current_session.messages.append({"role": "assistant", "content": reply})
            self.save_sessions()
        self.status_text = "Ready"

    def draw(self):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()

        # Sidebar with sessions
        sidebar_w = min(20, w // 5)
        if sidebar_w > 0:
            for i, s in enumerate(self.sessions):
                if i >= h - 2: break
                prefix = ">" if s is self.current_session else " "
                name = s.name[:sidebar_w - 2]
                try:
                    self.stdscr.addstr(i, 0, f"{prefix} {name}", curses.color_pair(1))
                except: pass

        # Title bar
        title = f" Keli Console - {self.current_session.name if self.current_session else 'No session'} "
        try:
            self.stdscr.addstr(0, sidebar_w, title, curses.color_pair(2) | curses.A_BOLD)
        except: pass

        # Output area
        max_y = h - 3
        output_start = 1
        visible = self.output_lines[-(max_y - output_start):]
        for i, line in enumerate(visible):
            if output_start + i > max_y: break
            try:
                self.stdscr.addstr(output_start + i, sidebar_w, str(line)[:w - sidebar_w - 1])
            except: pass

        # Input line
        input_y = h - 2
        prompt = "(search) " if self.search_mode else ">>> "
        try:
            self.stdscr.addstr(input_y, 0, prompt, curses.color_pair(3) | curses.A_BOLD)
            display = self.search_query if self.search_mode else self.input_buffer
            self.stdscr.addstr(input_y, len(prompt), str(display)[:w - len(prompt) - 1])
        except: pass

        # Status bar
        try:
            status = f" {self.status_text} | Sessions:{len(self.sessions)} | Ctrl+Q:Quit | Ctrl+N:New | Ctrl+D:Delete | Ctrl+R:Search "
            self.stdscr.addstr(h - 1, 0, status[:w - 1], curses.color_pair(2) | curses.A_BOLD)
        except: pass

        self.stdscr.refresh()

    def run_search(self):
        if not self.search_query:
            return
        self.search_results = [l for l in self.output_lines if self.search_query.lower() in l.lower()]
        self.search_idx = 0
        if self.search_results:
            self.status_text = f"Found {len(self.search_results)} matches"
        else:
            self.status_text = "No matches found"
        self.search_mode = False
        self.search_query = ""

    def run(self):
        while True:
            self.draw()
            key = self.stdscr.getch()

            if key == curses.KEY_RESIZE:
                continue

            if self.search_mode:
                if key == 27:  # ESC
                    self.search_mode = False
                    self.search_query = ""
                elif key in (10, 13):  # Enter
                    self.run_search()
                elif key == 127 or key == curses.KEY_BACKSPACE:
                    self.search_query = self.search_query[:-1]
                elif 32 <= key <= 126:
                    self.search_query += chr(key)
                continue

            if key == 17:  # Ctrl+Q
                break
            elif key == 14:  # Ctrl+N
                self.new_session()
            elif key == 4:  # Ctrl+D
                if self.current_session:
                    idx = self.sessions.index(self.current_session)
                    self.delete_session(idx)
            elif key == 18:  # Ctrl+R
                self.search_mode = True
                self.search_query = ""
                self.search_results = []
            elif key in (10, 13):  # Enter
                if self.input_buffer.strip():
                    if self.input_buffer.startswith("/"):
                        self.handle_command(self.input_buffer[1:])
                    else:
                        t = threading.Thread(target=self.send_message, args=(self.input_buffer,))
                        t.daemon = True
                        t.start()
                self.input_buffer = ""
            elif key == 27:  # ESC
                self.input_buffer = ""
            elif key == curses.KEY_UP:
                if self.history:
                    self.history_index = (self.history_index - 1) % len(self.history)
                    self.input_buffer = self.history[self.history_index]
            elif key == curses.KEY_DOWN:
                if self.history_index >= 0:
                    self.history_index = (self.history_index + 1) % len(self.history)
                    self.input_buffer = self.history[self.history_index]
                else:
                    self.input_buffer = ""
            elif key == curses.KEY_LEFT:
                pass
            elif key == curses.KEY_RIGHT:
                pass
            elif key == curses.KEY_NPAGE:
                pass
            elif key == curses.KEY_PPAGE:
                pass
            elif key == 9:  # Tab
                self.do_tab_complete()
            elif key == 127 or key == curses.KEY_BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
            elif 32 <= key <= 126:
                self.input_buffer += chr(key)

    def handle_command(self, cmd):
        parts = cmd.strip().split()
        if not parts:
            return
        if parts[0] == "help":
            self.output_lines.append("Commands: /help /new /delete /rename /theme /clear /quit")
        elif parts[0] == "new":
            self.new_session(" ".join(parts[1:]) if parts[1:] else None)
        elif parts[0] == "delete":
            if parts[1:]:
                try:
                    self.delete_session(int(parts[1]) - 1)
                except: pass
        elif parts[0] == "rename":
            if parts[1:] and self.current_session:
                self.current_session.name = " ".join(parts[1:])
                self.save_sessions()
        elif parts[0] == "theme":
            if parts[1:] and parts[1] in THEMES:
                os.environ["KELI_THEME"] = parts[1]
                self.status_text = f"Theme: {parts[1]}"
        elif parts[0] == "clear":
            self.output_lines = []
        elif parts[0] == "quit":
            raise SystemExit(0)

    def do_tab_complete(self):
        commands = ["help", "new", "delete", "rename", "theme", "clear", "quit"]
        if self.input_buffer.startswith("/"):
            partial = self.input_buffer[1:]
            matches = [c for c in commands if c.startswith(partial)]
            if len(matches) == 1:
                self.input_buffer = "/" + matches[0] + " "

def main():
    curses.wrapper(lambda stdscr: KeliTUI(stdscr).run())

if __name__ == "__main__":
    main()
TUI_PY_EOF
chmod +x "${KELI_LIB}/keli_tui.py"
log_ok "Created TUI module"

# Install the shell wrapper
cp "${SCRIPT_DIR}/keli-console.sh" "${KELI_HOME}/keli-console.sh"
chmod +x "${KELI_HOME}/keli-console.sh"
log_ok "Installed console shell wrapper"

# Create symlink
log_info "Setting up symlink..."
if [ "$(id -u)" -eq 0 ]; then
  ln -sf "${KELI_HOME}/keli-console.sh" /usr/local/bin/keli-console
else
  if command -v sudo >/dev/null 2>&1; then
    sudo ln -sf "${KELI_HOME}/keli-console.sh" /usr/local/bin/keli-console
  else
    mkdir -p "${KELI_HOME}/bin"
    ln -sf "${KELI_HOME}/keli-console.sh" "${KELI_HOME}/bin/keli-console"
    log_warn "Add ${KELI_HOME}/bin to PATH to use keli-console"
  fi
fi

log_ok "Console installation complete!"
echo ""
log_info "Usage: keli-console"
log_info "  Ctrl+N  - New session"
log_info "  Ctrl+D  - Delete session"
log_info "  Ctrl+R  - Search history"
log_info "  Ctrl+Q  - Quit"
log_info "  /help   - Show commands"
