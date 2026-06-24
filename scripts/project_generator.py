"""
Complete Project Generator — Keli outputs full, working multi-file projects.
Every project is runnable. Complete architectures, not snippets.
"""
import json, random, os
from pathlib import Path

class ProjectBlueprint:
    """A complete, working project blueprint with multiple files."""
    
    @staticmethod
    def todo_app():
        return {
            'name': 'todo-app',
            'description': 'Full-stack todo application with SQLite backend and React frontend',
            'territory': 'fullstack',
            'files': {
                'backend/app.py': """from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os, datetime

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)
DB = 'todo.db'

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            priority INTEGER DEFAULT 0
        )''')

init_db()

@app.route('/api/todos', methods=['GET'])
def get_todos():
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'DESC')
    with sqlite3.connect(DB) as conn:
        rows = conn.execute(f'SELECT * FROM todos ORDER BY {sort} {order}').fetchall()
        return jsonify([{
            'id': r[0], 'text': r[1], 'done': bool(r[2]),
            'created_at': r[3], 'priority': r[4]
        } for r in rows])

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    with sqlite3.connect(DB) as conn:
        cur = conn.execute('INSERT INTO todos (text, priority) VALUES (?, ?)',
                          (data['text'], data.get('priority', 0)))
        conn.commit()
        return jsonify({'id': cur.lastrowid}), 201

@app.route('/api/todos/<int:tid>', methods=['PUT'])
def update_todo(tid):
    data = request.get_json()
    with sqlite3.connect(DB) as conn:
        conn.execute('UPDATE todos SET done=? WHERE id=?',
                    (int(data.get('done', False)), tid))
        if 'text' in data:
            conn.execute('UPDATE todos SET text=? WHERE id=?', (data['text'], tid))
        conn.commit()
        return jsonify({'ok': True})

@app.route('/api/todos/<int:tid>', methods=['DELETE'])
def delete_todo(tid):
    with sqlite3.connect(DB) as conn:
        conn.execute('DELETE FROM todos WHERE id=?', (tid,))
        conn.commit()
        return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)''',
                'frontend/src/App.js': '''import React, { useState, useEffect } from 'react';
import './App.css';

const API = process.env.REACT_APP_API || 'http://localhost:5000/api';

function App() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  const [priority, setPriority] = useState(0);
  const [filter, setFilter] = useState('all');

  useEffect(() => { fetchTodos(); }, []);

  const fetchTodos = async () => {
    const res = await fetch(API + '/todos');
    setTodos(await res.json());
  };

  const addTodo = async () => {
    if (!input.trim()) return;
    await fetch(API + '/todos', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ text: input, priority })
    });
    setInput('');
    fetchTodos();
  };

  const toggleTodo = async (id, done) => {
    await fetch(API + '/todos/' + id, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ done: !done })
    });
    fetchTodos();
  };

  const deleteTodo = async (id) => {
    await fetch(API + '/todos/' + id, { method: 'DELETE' });
    fetchTodos();
  };

  const filtered = todos.filter(t => {
    if (filter === 'active') return !t.done;
    if (filter === 'done') return t.done;
    return true;
  });

  return (
    <div className="app">
      <h1>Keli Todo</h1>
      <div className="add-form">
        <input value={input} onChange={e => setInput(e.target.value)}
               onKeyDown={e => e.key === 'Enter' && addTodo()}
               placeholder="What needs to be done?" />
        <select value={priority} onChange={e => setPriority(Number(e.target.value))}>
          <option value={0}>Low</option>
          <option value={1}>Medium</option>
          <option value={2}>High</option>
        </select>
        <button onClick={addTodo}>Add</button>
      </div>
      <div className="filters">
        <button className={filter === 'all' ? 'active' : ''} onClick={() => setFilter('all')}>All</button>
        <button className={filter === 'active' ? 'active' : ''} onClick={() => setFilter('active')}>Active</button>
        <button className={filter === 'done' ? 'active' : ''} onClick={() => setFilter('done')}>Done</button>
      </div>
      <ul className="todo-list">
        {filtered.map(t => (
          <li key={t.id} className={'todo-item priority-' + t.priority + (t.done ? ' done' : '')}>
            <input type="checkbox" checked={t.done} onChange={() => toggleTodo(t.id, t.done)} />
            <span className="text">{t.text}</span>
            <span className="priority-badge">{['Low', 'Med', 'High'][t.priority]}</span>
            <button className="delete" onClick={() => deleteTodo(t.id)}>×</button>
          </li>
        ))}
      </ul>
      <p className="count">{todos.filter(t => !t.done).length} remaining</p>
    </div>
  );
}

export default App;''',
                'frontend/src/App.css': '''* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, sans-serif; background: #0a0a1a; color: #e0e0e0; max-width: 600px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; color: #00d4ff; margin-bottom: 20px; font-size: 2em; text-shadow: 0 0 10px rgba(0,212,255,0.5); }
.add-form { display: flex; gap: 8px; margin-bottom: 20px; }
.add-form input { flex: 1; padding: 12px; border: 1px solid #333; border-radius: 6px; background: #1a1a2e; color: #e0e0e0; font-size: 16px; }
.add-form input:focus { outline: none; border-color: #00d4ff; }
.add-form select { padding: 12px; border: 1px solid #333; border-radius: 6px; background: #1a1a2e; color: #e0e0e0; }
.add-form button { padding: 12px 24px; background: #00d4ff; color: #0a0a1a; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
.filters { display: flex; gap: 8px; margin-bottom: 16px; justify-content: center; }
.filters button { padding: 6px 16px; background: #1a1a2e; border: 1px solid #333; border-radius: 4px; color: #e0e0e0; cursor: pointer; }
.filters button.active { background: #00d4ff; color: #0a0a1a; border-color: #00d4ff; }
.todo-list { list-style: none; }
.todo-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: #1a1a2e; border: 1px solid #333; border-radius: 6px; margin-bottom: 8px; transition: all 0.2s; }
.todo-item:hover { border-color: #00d4ff; }
.todo-item.done .text { text-decoration: line-through; opacity: 0.5; }
.todo-item input[type="checkbox"] { width: 20px; height: 20px; cursor: pointer; }
.todo-item .text { flex: 1; }
.priority-badge { padding: 2px 8px; border-radius: 3px; font-size: 12px; }
.priority-2 .priority-badge { background: #ff4444; color: white; }
.priority-1 .priority-badge { background: #ffaa00; }
.priority-0 .priority-badge { background: #444; color: #ccc; }
.delete { background: none; border: none; color: #ff4444; font-size: 20px; cursor: pointer; }
.count { text-align: center; margin-top: 16px; color: #666; }''',
                'frontend/package.json': '''{
  "name": "todo-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}''',
                'docker-compose.yml': '''version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API=http://localhost:5000/api''',
                'README.md': '''# Todo App

Full-stack todo application built with Flask + React + SQLite.

## Quick Start
```bash
# Backend
cd backend && pip install flask flask-cors && python app.py

# Frontend
cd frontend && npm install && npm start
```

## Docker
```bash
docker-compose up
```

## API
- GET /api/todos - list all
- POST /api/todos - create
- PUT /api/todos/:id - update
- DELETE /api/todos/:id - delete
'''
            }
        }

    @staticmethod
    def chat_app():
        return {
            'name': 'realtime-chat',
            'description': 'Real-time chat application with WebSocket support',
            'territory': 'fullstack',
            'files': {
                'server.py': '''import asyncio
import websockets
import json
from datetime import datetime

clients = set()
nicknames = {}

async def broadcast(message, sender=None):
    if clients:
        msg = json.dumps(message)
        await asyncio.gather(
            *(c.send(msg) for c in clients if c != sender),
            return_exceptions=True
        )

async def handle(websocket):
    clients.add(websocket)
    try:
        nick = f"User{len(clients)}"
        nicknames[websocket] = nick
        await broadcast({"type": "join", "nick": nick, "users": [n for n in nicknames.values()]})
        async for raw in websocket:
            data = json.loads(raw)
            if data["type"] == "message":
                await broadcast({
                    "type": "message",
                    "nick": nicknames[websocket],
                    "text": data["text"],
                    "time": datetime.now().isoformat()
                })
            elif data["type"] == "nick":
                old = nicknames[websocket]
                nicknames[websocket] = data["nick"]
                await broadcast({"type": "nick", "old": old, "nick": data["nick"]})
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        if websocket in nicknames:
            await broadcast({"type": "leave", "nick": nicknames[websocket]})
            del nicknames[websocket]

async def main():
    print("Chat server on ws://0.0.0.0:8765")
    async with websockets.serve(handle, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())''',
                'client.html': '''<!DOCTYPE html>
<html>
<head><title>Keli Chat</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, sans-serif; background: #0a0a1a; color: #e0e0e0; height: 100vh; display: flex; flex-direction: column; }
#container { max-width: 600px; margin: 0 auto; width: 100%; display: flex; flex-direction: column; height: 100vh; }
header { text-align: center; padding: 16px; border-bottom: 1px solid #333; }
h1 { color: #00d4ff; font-size: 1.5em; text-shadow: 0 0 8px rgba(0,212,255,0.3); }
#status { color: #666; font-size: 12px; }
#messages { flex: 1; overflow-y: auto; padding: 16px; }
.msg { margin-bottom: 12px; padding: 10px; background: #1a1a2e; border-radius: 8px; border: 1px solid #333; }
.msg .nick { color: #00d4ff; font-weight: bold; font-size: 14px; }
.msg .time { color: #666; font-size: 11px; float: right; }
.msg .text { margin-top: 4px; }
.system { text-align: center; color: #666; font-size: 13px; margin: 8px 0; }
#input-area { display: flex; gap: 8px; padding: 16px; border-top: 1px solid #333; }
#input { flex: 1; padding: 12px; border: 1px solid #333; border-radius: 6px; background: #1a1a2e; color: #e0e0e0; }
#input:focus { outline: none; border-color: #00d4ff; }
#send { padding: 12px 24px; background: #00d4ff; color: #0a0a1a; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
</style></head>
<body>
<div id="container">
<header><h1>Keli Chat</h1><div id="status">Disconnected</div></header>
<div id="messages"></div>
<div id="input-area">
<input id="input" placeholder="Type a message..." />
<button id="send">Send</button>
</div></div>
<script>
const ws = new WebSocket("ws://localhost:8765");
const messages = document.getElementById("messages");
const input = document.getElementById("input");
const status = document.getElementById("status");

ws.onopen = () => status.textContent = "Connected";
ws.onclose = () => status.textContent = "Disconnected";

ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type === "message") {
        const div = document.createElement("div");
        div.className = "msg";
        div.innerHTML = \`<span class="nick">\${data.nick}</span><span class="time">\${data.time}</span><div class="text">\${data.text}</div>\`;
        messages.appendChild(div);
    } else if (data.type === "join") {
        addSystem(data.nick + " joined");
    } else if (data.type === "leave") {
        addSystem(data.nick + " left");
    }
    messages.scrollTop = messages.scrollHeight;
};

function addSystem(text) {
    const div = document.createElement("div");
    div.className = "system";
    div.textContent = text;
    messages.appendChild(div);
}

document.getElementById("send").onclick = () => {
    if (input.value.trim()) {
        ws.send(JSON.stringify({type: "message", text: input.value}));
        input.value = "";
    }
};
input.onkeydown = (e) => { if (e.key === "Enter") document.getElementById("send").click(); };
</script></body></html>''',
                'requirements.txt': 'websockets>=12.0',
                'README.md': '''# Real-time Chat

WebSocket-based chat server with HTML client.

## Run
```bash
pip install -r requirements.txt
python server.py
# Open client.html in browser
```
'''
            }
        }

    @staticmethod
    def game():
        return {
            'name': 'space-shooter',
            'description': 'Complete space shooter game with Pygame',
            'territory': 'python',
            'files': {
                'game.py': '''import pygame, random, math

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Keli Space Shooter")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

class Player:
    def __init__(self):
        self.x, self.y = W//2, H-60
        self.w, self.h = 40, 30
        self.speed = 5
        self.shoot_cooldown = 0
        self.lives = 3
        self.invincible = 0

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0: self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < W-self.w: self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0: self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < H-self.h: self.y += self.speed
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.invincible > 0: self.invincible -= 1

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 10
            return Bullet(self.x + self.w//2, self.y)
        return None

    def draw(self):
        if self.invincible % 4 < 2 or self.invincible == 0:
            pts = [(self.x, self.y+self.h), (self.x+self.w//2, self.y),
                   (self.x+self.w, self.y+self.h)]
            pygame.draw.polygon(screen, (0, 200, 255), pts)

class Bullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.speed = 8
        self.alive = True

    def update(self):
        self.y -= self.speed
        if self.y < 0: self.alive = False

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 4)

class Enemy:
    def __init__(self):
        self.x = random.randint(20, W-20)
        self.y = -20
        self.size = 15
        self.speed = random.uniform(1, 3)
        self.alive = True
        self.hp = 2 if random.random() < 0.2 else 1

    def update(self):
        self.y += self.speed
        if self.y > H + 20: self.alive = False

    def draw(self):
        color = (255, 100, 100) if self.hp > 1 else (200, 50, 50)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 20
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0: self.alive = False

    def draw(self):
        alpha = self.life / 20
        pygame.draw.circle(screen, (255, 200, 0, alpha), (int(self.x), int(self.y)), 3)

player = Player()
bullets = []
enemies = []
particles = []
score = 0
spawn_timer = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    keys = pygame.key.get_pressed()
    player.update(keys)

    if keys[pygame.K_SPACE]:
        b = player.shoot()
        if b: bullets.append(b)

    spawn_timer += 1
    if spawn_timer > max(20, 60 - score // 10):
        enemies.append(Enemy())
        spawn_timer = 0

    for b in bullets[:]:
        b.update()
        if not b.alive: bullets.remove(b)

    for e in enemies[:]:
        e.update()
        if not e.alive: enemies.remove(e)

    for b in bullets[:]:
        for e in enemies[:]:
            dx = b.x - e.x
            dy = b.y - e.y
            if math.hypot(dx, dy) < e.size + 4:
                b.alive = False
                e.hp -= 1
                if e.hp <= 0:
                    e.alive = False
                    score += 10
                    for _ in range(8):
                        particles.append(Particle(e.x, e.y))
                bullets.remove(b)
                break

    for e in enemies[:]:
        if (abs(player.x - e.x) < player.w//2 + e.size and
            abs(player.y - e.y) < player.h//2 + e.size):
            if player.invincible == 0:
                player.lives -= 1
                player.invincible = 60
                e.alive = False
                for _ in range(12):
                    particles.append(Particle(e.x, e.y))
                if player.lives <= 0:
                    running = False

    for p in particles[:]:
        p.update()
        if not p.alive: particles.remove(p)

    screen.fill((10, 10, 30))
    for _ in range(50):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        pygame.draw.circle(screen, (255, 255, 255, 50), (sx, sy), 1)

    player.draw()
    for b in bullets: b.draw()
    for e in enemies: e.draw()
    for p in particles: p.draw()

    score_text = font.render(f"Score: {score}", True, (200, 200, 200))
    screen.blit(score_text, (10, 10))
    lives_text = font.render(f"Lives: {player.lives}", True, (200, 200, 200))
    screen.blit(lives_text, (10, 50))

    pygame.display.flip()
    clock.tick(60)

screen.fill((10, 10, 30))
game_over = font.render("GAME OVER", True, (255, 50, 50))
screen.blit(game_over, (W//2 - 80, H//2 - 20))
final_score = font.render(f"Final Score: {score}", True, (200, 200, 200))
screen.blit(final_score, (W//2 - 80, H//2 + 20))
pygame.display.flip()
pygame.time.wait(2000)
pygame.quit()
''',
                'requirements.txt': 'pygame>=2.5.0',
                'README.md': '''# Space Shooter

A complete arcade space shooter built with Pygame.

## How to Run
```bash
pip install -r requirements.txt
python game.py
```

## Controls
- Arrow keys: Move
- Space: Shoot
- Destroy enemies, collect score, survive!
'''
            }
        }

    @staticmethod
    def api_framework():
        return {
            'name': 'nanobot-api-framework',
            'description': 'A novel API framework inspired by nanobot swarm architecture',
            'territory': 'python',
            'files': {
                'nanobot_api.py': '''"""
Nanobot API Framework — inspired by Keli's nanobot swarm architecture.
Each endpoint is a "nanobot" that votes on how to handle requests.
"""
import json, time, inspect, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import wraps
from typing import Callable, Any

class Nanobot:
    """A single API endpoint nanobot."""
    def __init__(self, name: str, handler: Callable, path: str, methods: list[str]):
        self.name = name
        self.handler = handler
        self.path = path
        self.methods = methods
        self.stats = {"calls": 0, "total_time": 0, "errors": 0, "last_call": None}
        self.confidence = 0.95

    def __call__(self, *args, **kwargs):
        self.stats["calls"] += 1
        self.stats["last_call"] = time.time()
        t0 = time.time()
        try:
            result = self.handler(*args, **kwargs)
            self.stats["total_time"] += time.time() - t0
            return result
        except Exception as e:
            self.stats["errors"] += 1
            self.confidence *= 0.9
            raise

    @property
    def avg_time(self):
        return self.stats["total_time"] / max(self.stats["calls"], 1)

class SwarmAPI:
    """A swarm of nanobot endpoints that collaborate."""

    def __init__(self, name="Keli Swarm API", version="1.0"):
        self.name = name
        self.version = version
        self.nanobots: list[Nanobot] = []
        self.middleware = []
        self.start_time = time.time()

    def endpoint(self, path: str, methods: list[str] = ["GET"],
                 name: str = None):
        """Decorator to register an endpoint nanobot."""
        def decorator(handler):
            bot_name = name or handler.__name__
            bot = Nanobot(bot_name, handler, path, methods)
            self.nanobots.append(bot)
            @wraps(handler)
            def wrapper(*args, **kwargs):
                return handler(*args, **kwargs)
            return bot
        return decorator

    def use(self, middleware_fn):
        """Add global middleware."""
        self.middleware.append(middleware_fn)

    def find_bot(self, path: str, method: str):
        """Find nanobot with highest confidence for this request."""
        candidates = [b for b in self.nanobots
                     if b.path == path and method in b.methods]
        if not candidates:
            return None
        return max(candidates, key=lambda b: b.confidence)

    def swarm_health(self):
        """Report health of all nanobots."""
        total_calls = sum(b.stats["calls"] for b in self.nanobots)
        total_errors = sum(b.stats["errors"] for b in self.nanobots)
        avg_conf = sum(b.confidence for b in self.nanobots) / max(len(self.nanobots), 1)
        uptime = time.time() - self.start_time
        return {
            "name": self.name,
            "version": self.version,
            "uptime_seconds": uptime,
            "nanobots": len(self.nanobots),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "average_confidence": round(avg_conf, 4),
            "status": "healthy" if avg_conf > 0.5 else "degraded",
            "bots": [{
                "name": b.name,
                "path": b.path,
                "methods": b.methods,
                "calls": b.stats["calls"],
                "errors": b.stats["errors"],
                "avg_time_ms": round(b.avg_time * 1000, 2),
                "confidence": round(b.confidence, 4)
            } for b in self.nanobots]
        }

# ---- Example app ----
api = SwarmAPI("Demo Nanobot API")

@api.endpoint("/", methods=["GET"])
def root():
    return {"service": api.name, "version": api.version, "status": "swarming"}

@api.endpoint("/echo", methods=["POST"])
def echo(data):
    return {"you_sent": data, "timestamp": time.time()}

@api.endpoint("/health", methods=["GET"])
def health():
    return api.swarm_health()

@api.endpoint("/compute", methods=["POST"])
def compute(payload):
    """Nanobot-powered computation cluster."""
    op = payload.get("operation", "sum")
    values = payload.get("values", [])
    if op == "sum": result = sum(values)
    elif op == "product":
        result = 1
        for v in values: result *= v
    elif op == "mean": result = sum(values) / max(len(values), 1)
    else: result = None
    return {"operation": op, "values": values, "result": result, "nanobot": "compute"}

class Handler(BaseHTTPRequestHandler):
    def _handle(self, method):
        body = None
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len > 0:
            body = json.loads(self.rfile.read(content_len))
        bot = api.find_bot(self.path, method)
        if bot is None:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())
            return
        try:
            result = bot(body) if body else bot()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self): self._handle("GET")
    def do_POST(self): self._handle("POST")
    def do_PUT(self): self._handle("PUT")
    def do_DELETE(self): self._handle("DELETE")

def run(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), Handler)
    print(api.swarm_health())
    print(f"Nanobot API running on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run()
''',
                'example_client.py': '''import requests, json

BASE = "http://localhost:8080"

# Root
r = requests.get(BASE + "/")
print("Root:", r.json())

# Echo
r = requests.post(BASE + "/echo", json={"hello": "nanobot"})
print("Echo:", r.json())

# Compute
r = requests.post(BASE + "/compute", json={"operation": "sum", "values": [1,2,3,4,5]})
print("Sum:", r.json())

r = requests.post(BASE + "/compute", json={"operation": "product", "values": [2,3,4]})
print("Product:", r.json())

# Health
r = requests.get(BASE + "/health")
health = r.json()
print(f"\nSwarm Health: {health['status']}")
print(f"Nanobots: {health['nanobots']}")
print(f"Avg Confidence: {health['average_confidence']}")
for bot in health['bots']:
    print(f"  {bot['name']}: {bot['calls']} calls, {bot['avg_time_ms']}ms, {bot['confidence']} confidence")
''',
                'requirements.txt': 'requests>=2.31.0',
                'README.md': '''# Nanobot API Framework

A novel API framework inspired by Keli's nanobot swarm architecture. Each endpoint is a "nanobot" with its own confidence, stats, and health metrics.

## Features
- Nanobot endpoints with confidence scoring
- Automatic health monitoring
- Swarm-level statistics
- Middleware support
- Built-in compute cluster

## Usage
```bash
python nanobot_api.py
python example_client.py
```
'''
            }
        }

    @staticmethod
    def security_suite():
        return {
            'name': 'security-audit-tool',
            'description': 'Complete security audit and vulnerability scanning toolkit',
            'territory': 'python',
            'files': {
                'security_audit.py': '''"""
Security Audit Toolkit — port scanning, vulnerability detection, password analysis.
"""
import socket, ssl, hashlib, re, json, concurrent.futures
from datetime import datetime
from urllib.parse import urlparse

class PortScanner:
    def __init__(self, timeout=1):
        self.timeout = timeout
        self.open_ports = []

    def check_port(self, host, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            result = s.connect_ex((host, port))
            s.close()
            if result == 0:
                service = self._guess_service(port)
                return port, service, "open"
        except:
            pass
        return None

    def _guess_service(self, port):
        services = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 445: "SMB", 3306: "MySQL",
            3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
            8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
        }
        return services.get(port, "Unknown")

    def scan(self, host, ports=None):
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445,
                    3306, 3389, 5432, 6379, 8080, 8443, 27017]
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            futures = {ex.submit(self.check_port, host, p): p for p in ports}
            for f in concurrent.futures.as_completed(futures):
                r = f.result()
                if r: results.append(r)
        return sorted(results, key=lambda x: x[0])

class PasswordAnalyzer:
    def __init__(self):
        self.common = ["password", "123456", "admin", "letmein",
                      "qwerty", "monkey", "dragon", "master"]

    def analyze(self, password):
        issues = []
        score = 0
        if len(password) < 8: issues.append("Too short (<8 chars)"); score -= 20
        elif len(password) >= 12: score += 20
        elif len(password) >= 16: score += 30

        if re.search(r'[a-z]', password): score += 10
        else: issues.append("Missing lowercase")

        if re.search(r'[A-Z]', password): score += 10
        else: issues.append("Missing uppercase")

        if re.search(r'\d', password): score += 10
        else: issues.append("Missing numbers")

        if re.search(r'[^a-zA-Z0-9]', password): score += 20
        else: issues.append("Missing special characters")

        if password.lower() in self.common: issues.append("Common password!"); score -= 50
        if password.lower() in [p * 2 for p in self.common if len(p) * 2 == len(password)]:
            issues.append("Pattern detected"); score -= 30

        entropy = self._entropy(password)
        if entropy < 30: issues.append("Low entropy")
        elif entropy > 60: score += 20

        level = "Strong" if score >= 70 else "Moderate" if score >= 40 else "Weak"
        return {"score": max(0, min(100, score)), "level": level,
                "entropy_bits": round(entropy, 1), "issues": issues}

    def _entropy(self, s):
        pool = 0
        if re.search(r'[a-z]', s): pool += 26
        if re.search(r'[A-Z]', s): pool += 26
        if re.search(r'\d', s): pool += 10
        if re.search(r'[^a-zA-Z0-9]', s): pool += 30
        if pool == 0: return 0
        return len(s) * (pool ** 0.5)

class SSLChecker:
    def check(self, hostname, port=443):
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        "hostname": hostname,
                        "port": port,
                        "valid": True,
                        "issuer": dict(cert.get("issuer", [])),
                        "subject": dict(cert.get("subject", [])),
                        "expires": cert.get("notAfter", "Unknown"),
                        "version": ssock.version()
                    }
        except Exception as e:
            return {"hostname": hostname, "port": port, "valid": False, "error": str(e)}

class SecurityAudit:
    def __init__(self):
        self.scanner = PortScanner()
        self.pwd_analyzer = PasswordAnalyzer()
        self.ssl_checker = SSLChecker()

    def audit_host(self, hostname):
        print(f"\\n=== Security Audit: {hostname} ===")
        print(f"Time: {datetime.now().isoformat()}\\n")

        ports = self.scanner.scan(hostname)
        print(f"Open Ports ({len(ports)}):")
        for p, svc, status in ports:
            risk = "HIGH" if p in [21, 23, 445, 3389] else "MEDIUM" if p in [22, 25, 3306] else "LOW"
            print(f"  Port {p}/{svc}: {status} [Risk: {risk}]")

        if 443 in [p[0] for p in ports]:
            print(f"\\nSSL Certificate Check:")
            ssl_result = self.ssl_checker.check(hostname)
            if ssl_result["valid"]:
                print(f"  Valid: YES")
                print(f"  Expires: {ssl_result['expires']}")
                print(f"  TLS Version: {ssl_result['version']}")
            else:
                print(f"  Valid: NO ({ssl_result.get('error', 'Unknown')})")

        print(f"\\nRecommendations:")
        high_risk = [p for p in ports if p[1] in ["FTP", "Telnet", "SMB", "RDP"]]
        if high_risk:
            for p, svc, _ in high_risk:
                print(f"  - Close port {p} ({svc}) - high security risk")
        print(f"  - Keep all systems updated")
        print(f"  - Use TLS 1.2+ for all services")
        print(f"  - Implement rate limiting")
        print(f"  - Enable audit logging")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    audit = SecurityAudit()
    audit.audit_host(target)

    print("\\n--- Password Strength Demo ---")
    for pwd in ["hello", "P@ssw0rd2024!", "123456", "MyC0mpl3x!P@ss"]:
        result = audit.pwd_analyzer.analyze(pwd)
        print(f"  '{pwd[:15]}...' -> {result['level']} ({result['score']}/100)")
''',
                'requirements.txt': '',
                'README.md': '''# Security Audit Toolkit

Port scanning, SSL checking, and password analysis in one suite.

## Usage
```bash
python security_audit.py [hostname]
python security_audit.py example.com
```
'''
            }
        }

    @staticmethod
    def microservice_arch():
        return {
            'name': 'event-mesh',
            'description': 'Event-driven microservice mesh with nanobot routing',
            'territory': 'python',
            'files': {
                'event_mesh.py': '''"""
Event Mesh — distributed event-driven microservice architecture.
Services communicate through events, not direct calls.
"""
import asyncio, json, uuid, time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any

@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    source: str = ""
    data: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""

@dataclass
class Service:
    name: str
    handlers: Dict[str, List[Callable]] = field(default_factory=dict)

    def on(self, event_type: str):
        def decorator(handler):
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)
            return handler
        return decorator

    async def handle(self, event: Event):
        handlers = self.handlers.get(event.type, [])
        results = []
        for h in handlers:
            result = h(event)
            if asyncio.iscoroutine(result):
                result = await result
            results.append(result)
        return results

class EventMesh:
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.event_log: List[Event] = []
        self.hooks: Dict[str, List[Callable]] = {}

    def register(self, service: Service):
        self.services[service.name] = service
        print(f"[Mesh] Service registered: {service.name}")

    def on_event(self, event_type: str):
        def decorator(handler):
            if event_type not in self.hooks:
                self.hooks[event_type] = []
            self.hooks[event_type].append(handler)
            return handler
        return decorator

    async def emit(self, event: Event):
        self.event_log.append(event)
        print(f"[Mesh] Event: {event.type} from {event.source}")

        # Global hooks
        for handler in self.hooks.get(event.type, []):
            result = handler(event)
            if asyncio.iscoroutine(result):
                await result

        # Service handlers
        tasks = []
        for service in self.services.values():
            handlers = service.handlers.get(event.type, [])
            for h in handlers:
                tasks.append(service.handle(event))
        if tasks:
            await asyncio.gather(*tasks)

    async def query(self, service_name: str, event_type: str, data: dict,
                    timeout: float = 5.0) -> Any:
        """Request-response pattern over events."""
        event = Event(type=event_type, source="query", data=data)
        service = self.services.get(service_name)
        if not service:
            raise ValueError(f"Service {service_name} not found")
        return await service.handle(event)

# ---- Example ----
mesh = EventMesh()

# Define services
user_service = Service("users")
order_service = Service("orders")
notification_service = Service("notifications")

@user_service.on("user.created")
def handle_user_created(event):
    print(f"  [Users] Creating user: {event.data}")
    return {"status": "created", "user_id": event.data.get("email")}

@order_service.on("order.placed")
async def handle_order_placed(event):
    print(f"  [Orders] Processing order: {event.data}")
    await mesh.emit(Event(type="notification.send", source="orders",
                         data={"type": "order_confirmation",
                               "user": event.data.get("user"),
                               "order_id": event.data.get("order_id")}))
    return {"status": "processing", "order_id": event.data.get("order_id")}

@notification_service.on("notification.send")
def handle_notification(event):
    print(f"  [Notifications] Sending {event.data['type']} to {event.data.get('user')}")
    return {"sent": True}

# Register
mesh.register(user_service)
mesh.register(order_service)
mesh.register(notification_service)

async def demo():
    print("\\n=== Event Mesh Demo ===\\n")

    await mesh.emit(Event(type="user.created", source="api",
                         data={"email": "test@example.com", "name": "Alice"}))

    await mesh.emit(Event(type="order.placed", source="api",
                         data={"order_id": "ORD-001", "user": "test@example.com",
                              "items": ["widget", "gadget"], "total": 49.99}))

    print(f"\\nEvent log: {len(mesh.event_log)} events processed")

if __name__ == "__main__":
    asyncio.run(demo())
''',
                'README.md': '''# Event Mesh

Event-driven microservice architecture with async routing.

## Run
```bash
python event_mesh.py
```
'''
            }
        }

    @staticmethod
    def keli_demo():
        return {
            'name': 'keli-swarm-demo',
            'description': 'Complete Keli nanobot swarm demo — shows architecture, confidence, and multi-territory generation',
            'territory': 'python',
            'files': {
                'swarm_demo.py': '''"""
Keli Swarm Demo — visualizes nanobot architecture, confidence scoring,
territory awareness, and multi-step reasoning.
"""
import random, time, json, math
from dataclasses import dataclass
from typing import List

@dataclass
class Nanobot:
    id: int
    territory: str
    confidence: float
    expertise: float
    emissions: List[str] = None

    def __post_init__(self):
        self.emissions = []

    def process(self, token: str, context: str) -> dict:
        relevance = self.expertise * random.uniform(0.8, 1.0)
        if token in context:
            relevance *= 1.5
        self.confidence = min(1.0, self.confidence * (0.95 + relevance * 0.05))
        emission = f"Bot{self.id}[{self.territory}]: token='{token}' conf={self.confidence:.3f}"
        self.emissions.append(emission)
        return {"bot_id": self.id, "territory": self.territory,
                "confidence": self.confidence, "relevance": relevance}

class NanobotSwarm:
    def __init__(self, n_bots=10000):
        self.territories = ["html", "css", "javascript", "python", "database"]
        self.bots = []
        for i in range(n_bots):
            terr = self.territories[i % len(self.territories)]
            exp = 0.3 + (i % 2000) / 2000 * 0.7
            self.bots.append(Nanobot(id=i, territory=terr,
                                     confidence=0.5 + random.random() * 0.3,
                                     expertise=exp))
        self.comm_rounds = 5
        self.router = {"html": 0, "css": 0, "javascript": 0,
                       "python": 0, "database": 0}

    def consensus(self, bot_outputs: List[dict]) -> dict:
        """Nanobots vote — weighted by confidence."""
        votes = {}
        for output in bot_outputs:
            terr = output["territory"]
            weight = output["confidence"] * output["relevance"]
            votes[terr] = votes.get(terr, 0) + weight
        total = sum(votes.values())
        if total == 0: return {"winner": "unknown", "distribution": votes}
        return {
            "winner": max(votes, key=votes.get),
            "distribution": {k: round(v/total, 4) for k, v in votes.items()}
        }

    def communicate(self):
        """Simulate communication rounds."""
        for r in range(self.comm_rounds):
            avg_conf = sum(b.confidence for b in self.bots) / len(self.bots)
            for b in self.bots:
                influence = avg_conf * random.uniform(0.1, 0.3)
                b.confidence = min(1.0, b.confidence + influence)
                b.confidence = max(0.1, b.confidence)

    def route(self, prompt: str) -> dict:
        """Route a prompt through the swarm."""
        tokens = prompt.lower().split()
        territory_map = {
            "html": ["html", "div", "tag", "element", "markup", "webpage"],
            "css": ["css", "style", "color", "layout", "font", "grid", "flex"],
            "javascript": ["js", "javascript", "function", "react", "vue",
                          "node", "event", "async", "fetch"],
            "python": ["python", "def", "class", "import", "flask",
                      "django", "algorithm", "data"],
            "database": ["sql", "database", "table", "query", "index",
                        "schema", "migration"]
        }

        for token in tokens:
            for terr, keywords in territory_map.items():
                if token in keywords:
                    self.router[terr] += 1

        # Activate bots by territory
        target_territory = max(self.router, key=self.router.get)
        active_bots = [b for b in self.bots if b.territory == target_territory]

        self.communicate()

        results = []
        for token in tokens[:5]:
            for bot in random.sample(active_bots, min(100, len(active_bots))):
                results.append(bot.process(token, prompt))

        consensus = self.consensus(results)
        avg_conf = sum(b.confidence for b in active_bots) / len(active_bots)
        top_bots = sorted(active_bots, key=lambda b: b.confidence, reverse=True)[:3]

        return {
            "prompt": prompt,
            "routed_to": target_territory,
            "territory_distribution": self.router,
            "territory": {t: round(c / max(sum(self.router.values()), 1), 4)
                         for t, c in self.router.items()},
            "nanobots_activated": len(active_bots),
            "average_confidence": round(avg_conf, 4),
            "consensus": consensus,
            "top_nanobots": [
                {"id": b.id, "territory": b.territory,
                 "confidence": round(b.confidence, 4),
                 "expertise": round(b.expertise, 4)}
                for b in top_bots
            ],
            "comm_rounds": self.comm_rounds,
        }

    def generate_code(self, prompt: str) -> dict:
        """Full pipeline: route -> generate -> confidence score."""
        routing = self.route(prompt)
        terr = routing["routed_to"]

        lines = {}
        lines["html"] = '<!DOCTYPE html>\n<html>\n<head><title>Keli Generated</title></head>\n<body>\n  <header><h1>Keli Swarm Output</h1></header>\n  <main><p>Generated by nanobot consensus (CONFIDENCE% confidence)</p></main>\n</body>\n</html>'
        lines["css"] = '/* Generated by Keli CSS Territory */\nbody {\n  background: linear-gradient(135deg, #0a0a1a, #1a1a3e);\n  color: #e0e0e0;\n  font-family: system-ui, sans-serif;\n  min-height: 100vh;\n}\n.neon-card {\n  background: #1a1a2e;\n  border: 1px solid #333;\n  border-radius: 12px;\n  padding: 24px;\n  box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);\n}'
        lines["javascript"] = '// Generated by Keli JS Territory\nconst swarm = {\n  bots: 10000,\n  confidence: 0.95,\n  async generate(prompt) {\n    const response = await this.route(prompt);\n    return this.assemble(response);\n  },\n  route(prompt) {\n    const territories = ["html","css","js","python","db"];\n    const scores = territories.map(t => ({\n      territory: t,\n      score: Math.random() * (t === "javascript" ? 0.9 : 0.5)\n    }));\n    return scores.reduce((a, b) => a.score > b.score ? a : b);\n  },\n  assemble(routing) {\n    return { status: "complete", territory: routing.territory };\n  }\n};'
        lines["python"] = '# Generated by Keli Python Territory\nfrom dataclasses import dataclass\nfrom typing import List\nimport random\n\n@dataclass\nclass SwarmOutput:\n    code: str\n    confidence: float\n    territory: str\n\nclass KeliGenerator:\n    def __init__(self):\n        self.territories = ["html", "css", "js", "python", "db"]\n        self.confidence = 0.95\n\n    def generate(self, prompt: str) -> SwarmOutput:\n        terr = self._route(prompt)\n        code = self._produce(terr, prompt)\n        return SwarmOutput(code, self.confidence, terr)\n\n    def _route(self, prompt: str) -> str:\n        scores = {t: random.random() for t in self.territories}\n        scores["python"] *= 1.5\n        return max(scores, key=scores.get)\n\n    def _produce(self, territory: str, prompt: str) -> str:\n        return "# " + territory.upper() + " output for: " + prompt + "\\nprint(\'Hello from Keli!\')"'
        lines["database"] = '-- Generated by Keli DB Territory\nCREATE TABLE IF NOT EXISTS swarm_outputs (\n    id SERIAL PRIMARY KEY,\n    prompt TEXT NOT NULL,\n    territory VARCHAR(20) NOT NULL,\n    code TEXT,\n    confidence DECIMAL(5,4),\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n\nCREATE INDEX idx_territory ON swarm_outputs(territory);\nCREATE INDEX idx_confidence ON swarm_outputs(confidence DESC);\n\nCREATE VIEW active_swarm AS\nSELECT territory, COUNT(*) as bot_count, AVG(confidence) as avg_confidence\nFROM swarm_outputs\nGROUP BY territory;'

        code = lines.get(terr, "# Generated by Keli Swarm")
        confidence_pct = round(routing["average_confidence"] * 100, 1)
        code = code.replace("CONFIDENCE", str(confidence_pct))
        code = code.replace("{confidence}", str(confidence_pct))

        return {
            "routing": routing,
            "code": code,
            "confidence": routing["average_confidence"],
            "language": terr,
            "lines": len(code.split("\\n"))
        }

if __name__ == "__main__":
    print("=== Keli Nanobot Swarm Demo ===\\n")

    swarm = NanobotSwarm(10000)
    print(f"Swarm initialized with {len(swarm.bots)} nanobots")
    print(f"Territories: {', '.join(swarm.territories)}\\n")

    prompts = [
        "build a react component with grid layout and python backend",
        "create a flask api with sqlite database",
        "design a responsive website with animations"
    ]

    for prompt in prompts:
        print(f"Prompt: {prompt}")
        print("-" * 50)
        result = swarm.generate_code(prompt)
        print(f"Routed to: {result['routing']['routed_to']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Top nanobots:")
        for bot in result['routing']['top_nanobots']:
            print(f"  Bot {bot['id']}: {bot['territory']} "
                  f"(conf: {bot['confidence']:.2%}, exp: {bot['expertise']:.2%})")
        print(f"Territory distribution: {result['routing']['territory']}")
        print(f"Generated code ({result['language']}):")
        for line in result['code'].split("\\n"):
            print(f"  {line}")
        print()
''',
                'README.md': '''# Keli Swarm Demo

Interactive demo of Keli's nanobot swarm architecture.

## Run
```bash
python swarm_demo.py
```

Shows: routing, confidence scoring, territory distribution, code generation
'''
            }
        }

    @staticmethod
    def all_blueprints():
        return [
            ProjectBlueprint.todo_app(),
            ProjectBlueprint.chat_app(),
            ProjectBlueprint.game(),
            ProjectBlueprint.api_framework(),
            ProjectBlueprint.security_suite(),
            ProjectBlueprint.microservice_arch(),
            ProjectBlueprint.keli_demo(),
        ]


def projects_to_training_data(blueprints, copies=1000):
    """Convert project blueprints to training examples."""
    examples = []
    for bp in blueprints:
        for filename, code in bp['files'].items():
            prompt = f"generate a {bp['name']} {filename}"
            examples.append({"input": prompt, "target": code})

            prompt2 = f"build the {bp['name']} project"
            all_files = "\n".join(f"--- {f} ---\n{c}" for f, c in bp['files'].items())
            examples.append({"input": prompt2, "target": all_files})

            for _ in range(8):
                var_prompt = f"create {bp['territory']} code for {bp['name']}"
                examples.append({"input": var_prompt, "target": code})

    return examples

if __name__ == "__main__":
    bps = ProjectBlueprint.all_blueprints()
    examples = projects_to_training_data(bps, copies=10000)
    print(f"Generated {len(examples)} training examples from {len(bps)} blueprints")
    for bp in bps:
        file_count = len(bp['files'])
        lines = sum(len(c.split("\\n")) for c in bp['files'].values())
        print(f"  {bp['name']}: {file_count} files, {lines} lines of working code")
