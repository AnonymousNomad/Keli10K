#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/keli-config.sh"

log_step "Installing Keli Desktop"

ensure_dirs

KELI_LIB="${KELI_HOME}/lib/desktop"
mkdir -p "$KELI_LIB"

# Create desktop server stub
cat > "${KELI_LIB}/server.py" << 'SRV_PY_EOF'
#!/usr/bin/env python3
"""Keli Desktop - Web server for the desktop GUI frontend."""
import argparse, http.server, json, os, sys, urllib.request
from urllib.parse import urlparse, parse_qs

KELI_API = os.environ.get("KELI_API", "http://localhost:8085")
KELI_MEMORY = os.environ.get("KELI_MEMORY", "http://localhost:9090")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Keli Desktop</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:system-ui,-apple-system,sans-serif}
body{background:#1a1a2e;color:#eee;height:100vh;display:flex;flex-direction:column}
header{background:#16213e;padding:16px 24px;display:flex;align-items:center;gap:16px;border-bottom:1px solid #0f3460}
header h1{font-size:20px;color:#e94560;flex:1}
.tray-btn{background:0;border:1px solid #0f3460;color:#eee;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:13px}
.tray-btn:hover{background:#0f3460}
.chat-area{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:80%;padding:12px 16px;border-radius:12px;line-height:1.5;animation:fadeIn .2s}
.msg.user{background:#0f3460;align-self:flex-end;border-bottom-right-radius:4px}
.msg.assistant{background:#16213e;align-self:flex-start;border-bottom-left-radius:4px}
.msg .role{font-size:11px;color:#888;margin-bottom:4px}
.msg pre{background:#111;padding:8px;border-radius:6px;overflow-x:auto;margin-top:6px}
.input-area{background:#16213e;padding:16px 24px;display:flex;gap:12px;border-top:1px solid #0f3460}
.input-area textarea{flex:1;background:#1a1a2e;border:1px solid #0f3460;border-radius:8px;padding:12px;color:#eee;resize:none;font-size:14px;min-height:48px;max-height:150px}
.input-area textarea:focus{outline:0;border-color:#e94560}
.input-area button{background:#e94560;border:0;color:#fff;padding:12px 24px;border-radius:8px;cursor:pointer;font-size:14px;font-weight:600}
.input-area button:hover{background:#c73650}
.status-bar{background:#0f3460;padding:8px 24px;font-size:12px;color:#888;display:flex;gap:24px}
.status-bar span{display:flex;align-items:center;gap:6px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot.green{background:#4ade80}
.dot.red{background:#f87171}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
#tray-dropdown{display:none;position:absolute;top:60px;right:24px;background:#16213e;border:1px solid #0f3460;border-radius:8px;padding:8px;min-width:160px;z-index:100}
#tray-dropdown.show{display:block}
#tray-dropdown button{display:block;width:100%;background:0;border:0;color:#eee;padding:8px 12px;text-align:left;cursor:pointer;border-radius:4px;font-size:14px}
#tray-dropdown button:hover{background:#0f3460}
</style>
</head>
<body>
<header>
<h1>Keli Desktop</h1>
<button class="tray-btn" onclick="toggleTray()">&#x22EE;</button>
<div id="tray-dropdown">
<button onclick="toggleAutoStart()">Toggle Auto-Start</button>
<button onclick="notify('Keli','Desktop is running')">Test Notification</button>
<button onclick="window.close()">Quit</button>
</div>
</header>
<div class="chat-area" id="chat"></div>
<div class="input-area">
<textarea id="input" placeholder="Ask Keli anything..." rows="1" onkeydown="if(event.key=='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
<button onclick="send()">Send</button>
</div>
<div class="status-bar">
<span><span class="dot green" id="apidot"></span> API</span>
<span id="model-label">Model: default</span>
<span id="session-label">Session: 1</span>
</div>
<script>
let sessionId = Date.now().toString();
function toggleTray(){document.getElementById('tray-dropdown').classList.toggle('show')}
document.addEventListener('click',function(e){let t=document.getElementById('tray-dropdown');if(!e.target.closest('.tray-btn')&&!e.target.closest('#tray-dropdown'))t.classList.remove('show')});
function addMsg(role,content){let d=document.getElementById('chat');let m=document.createElement('div');m.className='msg '+role;let r=document.createElement('div');r.className='role';r.textContent=role;m.appendChild(r);let c=document.createElement('div');c.textContent=content;m.appendChild(c);d.appendChild(m);d.scrollTop=d.scrollHeight}
async function send(){let t=document.getElementById('input');let p=t.value.trim();if(!p)return;t.value='';addMsg('user',p);t.disabled=1;try{let r=await fetch('/api/chat',{method:'POST',body:JSON.stringify({prompt:p,session:sessionId}),headers:{'Content-Type':'application/json'}});let d=await r.json();addMsg('assistant',d.response||JSON.stringify(d))}catch(e){addMsg('assistant','Error: '+e.message)}t.disabled=0;t.focus()}
function notify(t,b){if('Notification' in window){Notification.requestPermission().then(function(p){if(p==='granted')new Notification(t,{body:b})})}}
function toggleAutoStart(){fetch('/api/autostart').then(r=>r.json()).then(d=>alert(d.message||'Toggled'))}
</script>
</body>
</html>"""

class KeliDesktopHTTPHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode())
        elif parsed.path == "/api/status":
            self.send_json({"status": "ok", "session": "active"})
        elif parsed.path == "/api/autostart":
            self.send_json({"message": "Auto-start toggled (simulated)"})
        elif parsed.path == "/api/sessions":
            self.send_json({"sessions": [{"id": "1", "name": "Default"}], "current": "1"})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode() if content_len else "{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

        if parsed.path == "/api/chat":
            prompt = data.get("prompt", "")
            try:
                req_data = json.dumps({"prompt": prompt, "stream": False}).encode()
                req = urllib.request.Request(f"{KELI_API}/chat", data=req_data,
                                             headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    resp = json.loads(r.read().decode())
                self.send_json(resp)
            except Exception as e:
                self.send_json({"response": f"[Keli Desktop] {e}"})
        else:
            self.send_json({"error": "not found"})

    def send_json(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

def main():
    parser = argparse.ArgumentParser(description="Keli Desktop Server")
    parser.add_argument("--port", type=int, default=int(os.environ.get("KELI_PORT", 8085)))
    args = parser.parse_args()
    server = http.server.HTTPServer(("127.0.0.1", args.port), KeliDesktopHTTPHandler)
    print(f"Keli Desktop running on http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
SRV_PY_EOF
chmod +x "${KELI_LIB}/server.py"
log_ok "Created desktop server"

# Install shell wrapper
cp "${SCRIPT_DIR}/keli-desktop.sh" "${KELI_HOME}/keli-desktop.sh"
chmod +x "${KELI_HOME}/keli-desktop.sh"
log_ok "Installed desktop shell wrapper"

# Create symlink
if [ "$(id -u)" -eq 0 ]; then
  ln -sf "${KELI_HOME}/keli-desktop.sh" /usr/local/bin/keli-desktop
else
  if command -v sudo >/dev/null 2>&1; then
    sudo ln -sf "${KELI_HOME}/keli-desktop.sh" /usr/local/bin/keli-desktop
  else
    mkdir -p "${KELI_HOME}/bin"
    ln -sf "${KELI_HOME}/keli-desktop.sh" "${KELI_HOME}/bin/keli-desktop"
    log_warn "Add ${KELI_HOME}/bin to PATH to use keli-desktop"
  fi
fi

# Install .desktop file
log_info "Installing .desktop file..."
DESKTOP_DIR="${HOME}/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
cp "${SCRIPT_DIR}/keli.desktop" "${DESKTOP_DIR}/keli.desktop"
log_ok "Installed .desktop file to ${DESKTOP_DIR}"

# Install icon
ICON_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$ICON_DIR"
if [ -f "${SCRIPT_DIR}/keli.svg" ]; then
  cp "${SCRIPT_DIR}/keli.svg" "${ICON_DIR}/keli.svg"
  log_ok "Installed app icon"
fi

# Auto-start
AUTOSTART_DIR="${HOME}/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cat > "${AUTOSTART_DIR}/keli.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Keli Desktop
Exec=${KELI_HOME}/keli-desktop.sh start
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
log_ok "Set up auto-start in ${AUTOSTART_DIR}"

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_DIR}" 2>/dev/null || true
fi

log_ok "Desktop installation complete!"
echo ""
log_info "Usage: keli-desktop start   (starts server and opens browser)"
log_info "       keli-desktop stop"
log_info "       keli-desktop status"
log_info ""
log_info "Web UI: http://localhost:${KELI_PORT:-8085}"
