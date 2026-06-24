import random
import json
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snca_tokenizer import SNCATokenizer

tokenizer = SNCATokenizer()
SPECIAL = {
    'BOS': tokenizer.bos_id, 'EOS': tokenizer.eos_id,
    'PAD': tokenizer.pad_id, 'UNK': tokenizer.unk_id,
}

def tokenize(text):
    return tokenizer.encode(text, bos=False, eos=False)

FRONTEND_HTML = [
    {
        "prompt": "Create a semantic HTML5 page structure with header, nav, main, article, section, footer",
        "code": '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page</title></head><body><header><nav><ul><li><a href="/">Home</a></li><li><a href="/about">About</a></li></ul></nav></header><main><article><section><h1>Welcome</h1><p>Content here</p></section></article></main><footer><p>&copy; 2026</p></footer></body></html>'
    },
    {
        "prompt": "Build an accessible form with fields for name, email, password, and a submit button",
        "code": '<form action="/submit" method="POST" aria-label="Registration"><label for="name">Name</label><input type="text" id="name" name="name" required aria-required="true"><label for="email">Email</label><input type="email" id="email" name="email" required><label for="password">Password</label><input type="password" id="password" name="password" minlength="8" required><button type="submit" aria-label="Submit form">Register</button></form>'
    },
    {
        "prompt": "Create a responsive data table with headers, caption, and row striping",
        "code": '<table role="table" aria-label="User data"><caption>User accounts overview</caption><thead><tr><th scope="col">ID</th><th scope="col">Name</th><th scope="col">Role</th><th scope="col">Status</th></tr></thead><tbody><tr><td>1</td><td>Alice Chen</td><td>Admin</td><td>Active</td></tr><tr><td>2</td><td>Bob Martinez</td><td>Editor</td><td>Pending</td></tr></tbody></table>'
    },
]

FRONTEND_CSS = [
    {
        "prompt": "Build a responsive layout using CSS Grid with sidebar and main content area",
        "code": ".layout{display:grid;grid-template-columns:250px 1fr;grid-template-rows:auto 1fr auto;min-height:100vh}.sidebar{grid-column:1;grid-row:1/4;background:#1a1a2e;padding:1rem}.main{grid-column:2;grid-row:2;padding:2rem}.header{grid-column:2;grid-row:1}.footer{grid-column:2;grid-row:3}@media(max-width:768px){.layout{grid-template-columns:1fr}.sidebar{grid-column:1;grid-row:auto}}"
    },
    {
        "prompt": "Create a flexbox navbar with centered navigation links and right-aligned CTA button",
        "code": ".navbar{display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.1)}.nav-links{display:flex;gap:1.5rem;list-style:none}.nav-links a{text-decoration:none;color:#333;font-weight:500}.cta-btn{background:#0066ff;color:#fff;padding:0.5rem 1.25rem;border-radius:6px;transition:all 0.2s}.cta-btn:hover{background:#0052cc;transform:translateY(-1px)}"
    },
    {
        "prompt": "Build animated card hover effect with transform and box-shadow transitions",
        "code": ".card{background:#fff;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);transition:all 0.3s cubic-bezier(0.4,0,0.2,1)}.card:hover{transform:translateY(-4px);box-shadow:0 12px 24px rgba(0,0,0,0.12)}.card img{width:100%;height:200px;object-fit:cover;border-radius:8px;transition:transform 0.3s}.card:hover img{transform:scale(1.05)}"
    },
]

FRONTEND_JS = [
    {
        "prompt": "Write async function to fetch user data from an API with error handling",
        "code": "async function fetchUserData(userId) { try { const response = await fetch(`https://api.example.com/users/${userId}`); if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`); const data = await response.json(); return { success: true, user: data }; } catch (error) { console.error('Fetch failed:', error.message); return { success: false, error: error.message }; } }"
    },
    {
        "prompt": "Implement debounce function for search input optimization",
        "code": "function debounce(fn, delay = 300) { let timer; return function(...args) { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay); }; } const searchInput = document.getElementById('search'); const handleSearch = debounce(async (event) => { const query = event.target.value.trim(); if (query.length < 2) return; const results = await fetchSearchResults(query); renderResults(results); }, 400); searchInput.addEventListener('input', handleSearch);"
    },
    {
        "prompt": "Use array methods map, filter, reduce to transform a dataset",
        "code": "const users = [{name:'Alice',age:32,active:true},{name:'Bob',age:28,active:false},{name:'Charlie',age:45,active:true}]; const activeNames = users.filter(u => u.active).map(u => u.name); const totalAge = users.reduce((sum, u) => sum + u.age, 0); const avgAge = totalAge / users.length; const groupedByActive = users.reduce((acc, u) => { const key = u.active ? 'active' : 'inactive'; acc[key] = acc[key] || []; acc[key].push(u); return acc; }, {});"
    },
]

FRONTEND_REACT = [
    {
        "prompt": "Create a React counter component with useState and useEffect for document title",
        "code": "import React, { useState, useEffect } from 'react'; function Counter() { const [count, setCount] = useState(0); useEffect(() => { document.title = `Count: ${count}`; return () => { document.title = 'React App'; }; }, [count]); return (<div className='counter'><h2>Count: {count}</h2><button onClick={() => setCount(c => c + 1)}>Increment</button><button onClick={() => setCount(c => c - 1)}>Decrement</button><button onClick={() => setCount(0)}>Reset</button></div>); }"
    },
    {
        "prompt": "Build a custom useFetch hook for API data fetching with loading and error states",
        "code": "import { useState, useEffect } from 'react'; function useFetch(url) { const [data, setData] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState(null); useEffect(() => { let cancelled = false; async function fetchData() { try { setLoading(true); const response = await fetch(url); if (!response.ok) throw new Error(`HTTP ${response.status}`); const result = await response.json(); if (!cancelled) setData(result); } catch (err) { if (!cancelled) setError(err.message); } finally { if (!cancelled) setLoading(false); } } fetchData(); return () => { cancelled = true; }; }, [url]); return { data, loading, error }; }"
    },
    {
        "prompt": "Create a TodoApp component with add, toggle, and delete functionality using useReducer",
        "code": "import React, { useReducer, useState } from 'react'; function todoReducer(state, action) { switch (action.type) { case 'ADD': return [...state, { id: Date.now(), text: action.payload, completed: false }]; case 'TOGGLE': return state.map(t => t.id === action.payload ? { ...t, completed: !t.completed } : t); case 'DELETE': return state.filter(t => t.id !== action.payload); default: return state; } } function TodoApp() { const [todos, dispatch] = useReducer(todoReducer, []); const [input, setInput] = useState(''); const addTodo = () => { if (input.trim()) { dispatch({ type: 'ADD', payload: input.trim() }); setInput(''); } }; return (<div className='todo-app'><h1>Todo List</h1><div className='add-todo'><input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && addTodo()} placeholder='Add a task...'/><button onClick={addTodo}>Add</button></div><ul>{todos.map(todo => (<li key={todo.id} className={todo.completed ? 'completed' : ''}><span onClick={() => dispatch({ type: 'TOGGLE', payload: todo.id })}>{todo.text}</span><button onClick={() => dispatch({ type: 'DELETE', payload: todo.id })}>Delete</button></li>))}</ul></div>); }"
    },
]

BACKEND_PYTHON = [
    {
        "prompt": "Write a Python decorator that measures function execution time",
        "code": "import time import functools def timer(func): @functools.wraps(func) def wrapper(*args, **kwargs): start = time.perf_counter() result = func(*args, **kwargs) elapsed = time.perf_counter() - start print(f'{func.__name__} took {elapsed:.4f}s') return result return wrapper @timer def process_data(items): return [item ** 2 for item in items]"
    },
    {
        "prompt": "Create a FastAPI endpoint with request validation, error handling, and pagination",
        "code": "from fastapi import FastAPI, HTTPException, Query from pydantic import BaseModel from typing import Optional import databases app = FastAPI(title='User API') class UserCreate(BaseModel): name: str email: str role: str = 'user' class UserResponse(BaseModel): id: int name: str email: str role: str @app.post('/api/users', response_model=UserResponse, status_code=201) async def create_user(user: UserCreate): if not user.email or '@' not in user.email: raise HTTPException(400, 'Invalid email') try: query = 'INSERT INTO users (name, email, role) VALUES (:name, :email, :role) RETURNING id' values = {'name': user.name, 'email': user.email, 'role': user.role} user_id = await database.execute(query=query, values=values) return {**user.dict(), 'id': user_id} except Exception as e: raise HTTPException(500, f'Database error: {str(e)}') @app.get('/api/users') async def list_users(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)): offset = (page - 1) * per_page query = 'SELECT * FROM users LIMIT :limit OFFSET :offset' users = await database.fetch_all(query=query, values={'limit': per_page, 'offset': offset}) return {'users': users, 'page': page, 'per_page': per_page, 'total': len(users)}"
    },
    {
        "prompt": "Implement a generator-based data pipeline that processes large files line by line",
        "code": "def read_large_file(filepath): with open(filepath, 'r', encoding='utf-8') as f: for line in f: yield line.strip() def parse_csv_line(line): if not line or line.startswith('#'): return None return line.split(',') def filter_valid(records): for rec in records: if rec and len(rec) >= 3: yield rec def transform_pipeline(filepath): raw = read_large_file(filepath) parsed = (parse_csv_line(line) for line in raw) valid = filter_valid(parsed) for rec in valid: yield {'id': int(rec[0]), 'name': rec[1], 'value': float(rec[2])}"
    },
]

BACKEND_API = [
    {
        "prompt": "Build a Flask REST API with JWT authentication, CRUD endpoints, and rate limiting",
        "code": "from flask import Flask, request, jsonify from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity from flask_limiter import Limiter from datetime import timedelta import bcrypt app = Flask(__name__) app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'dev-secret-change-in-prod') jwt = JWTManager(app) limiter = Limiter(app, key_func=lambda: request.remote_addr) @app.route('/api/auth/login', methods=['POST']) def login(): data = request.get_json() if not data or not data.get('email') or not data.get('password'): return jsonify({'error': 'Email and password required'}), 400 user = find_user_by_email(data['email']) if not user or not bcrypt.checkpw(data['password'].encode(), user['password_hash'].encode()): return jsonify({'error': 'Invalid credentials'}), 401 token = create_access_token(identity=user['id'], expires_delta=timedelta(hours=2)) return jsonify({'token': token, 'user': {'id': user['id'], 'email': user['email'], 'name': user['name']}}) @app.route('/api/projects', methods=['GET']) @jwt_required() @limiter.limit('120 per minute') def list_projects(): user_id = get_jwt_identity() page = request.args.get('page', 1, type=int) per_page = request.args.get('per_page', 20, type=int) projects = get_projects_by_user(user_id, page, per_page) return jsonify({'projects': projects, 'page': page, 'per_page': per_page}) @app.route('/api/projects', methods=['POST']) @jwt_required() def create_project(): data = request.get_json() if not data or not data.get('name'): return jsonify({'error': 'Project name required'}), 400 user_id = get_jwt_identity() project = insert_project(name=data['name'], description=data.get('description', ''), user_id=user_id) return jsonify(project), 201 @app.errorhandler(429) def ratelimit_handler(e): return jsonify({'error': 'Rate limit exceeded', 'retry_after': e.description}), 429"
    },
    {
        "prompt": "Create a SQLAlchemy async database session manager with connection pooling",
        "code": "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker from sqlalchemy.orm import declarative_base from typing import AsyncGenerator import os DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///./app.db') engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20, pool_pre_ping=True) AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) Base = declarative_base() async def get_db() -> AsyncGenerator[AsyncSession, None]: async with AsyncSessionLocal() as session: try: yield session await session.commit() except Exception: await session.rollback() raise async def init_db(): async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)"
    },
]

DESIGN_LAYOUT = [
    {
        "prompt": "Build a responsive mobile-first layout with CSS Grid, containers, and breakpoints",
        "code": ":root{--primary:#2563eb;--secondary:#7c3aed;--bg:#f8fafc;--text:#1e293b;--spacing:1rem}*{box-sizing:border-box;margin:0;padding:0}body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}.container{width:100%;padding:0 var(--spacing);margin:0 auto}.grid{display:grid;gap:var(--spacing);grid-template-columns:1fr}@media(min-width:640px){.container{max-width:640px}.grid{grid-template-columns:repeat(2,1fr)}}@media(min-width:768px){.container{max-width:768px}.grid{grid-template-columns:repeat(3,1fr)}}@media(min-width:1024px){.container{max-width:1024px}.grid{grid-template-columns:repeat(4,1fr)}}"
    },
    {
        "prompt": "Create a color system with CSS custom properties following WCAG AA contrast ratios",
        "code": ":root{--color-primary:#1a56db;--color-primary-hover:#1648c0;--color-primary-light:#e8effd;--color-secondary:#6b21a8;--color-success:#057a55;--color-warning:#b45309;--color-danger:#dc2626;--color-info:#1e40af;--text-primary:#111827;--text-secondary:#4b5563;--text-inverse:#ffffff;--bg-primary:#ffffff;--bg-secondary:#f3f4f6;--bg-tertiary:#e5e7eb;--border:#d1d5db;--radius-sm:4px;--radius-md:8px;--radius-lg:12px;--shadow-sm:0 1px 2px rgba(0,0,0,0.05);--shadow-md:0 4px 6px rgba(0,0,0,0.07);--shadow-lg:0 10px 15px rgba(0,0,0,0.1)}[data-theme='dark']{--text-primary:#f9fafb;--text-secondary:#d1d5db;--bg-primary:#111827;--bg-secondary:#1f2937;--bg-tertiary:#374151;--border:#4b5563}"
    },
]

DESIGN_ANIMATION = [
    {
        "prompt": "Build a CSS keyframe loading spinner animation with custom timing",
        "code": "@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}.spinner{width:40px;height:40px;border:4px solid #e5e7eb;border-top-color:#3b82f6;border-radius:50%;animation:spin 0.8s linear infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}.pulse{animation:pulse 2s cubic-bezier(0.4,0,0.6,1) infinite}@keyframes slideIn{from{transform:translateX(-100%);opacity:0}to{transform:translateX(0);opacity:1}}.slide-in{animation:slideIn 0.3s ease-out}"
    },
    {
        "prompt": "Create a Canvas-based particle animation system with mouse interaction",
        "code": "class ParticleSystem{constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d');this.particles=[];this.mouse={x:null,y:null};this.init()}init(){this.resize();window.addEventListener('resize',()=>this.resize());this.canvas.addEventListener('mousemove',(e)=>{this.mouse.x=e.clientX;this.mouse.y=e.clientY});for(let i=0;i<100;i++){this.particles.push(new Particle(this.canvas.width,this.canvas.height))}this.animate()}resize(){this.canvas.width=window.innerWidth;this.canvas.height=window.innerHeight}animate(){this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);this.particles.forEach(p=>{p.update(this.mouse);p.draw(this.ctx);this.connectParticles(p)});requestAnimationFrame(()=>this.animate())}connectParticles(p){this.particles.forEach(other=>{const dx=p.x-other.x;const dy=p.y-other.y;const dist=Math.sqrt(dx*dx+dy*dy);if(dist<120){this.ctx.beginPath();this.ctx.moveTo(p.x,p.y);this.ctx.lineTo(other.x,other.y);this.ctx.strokeStyle=`rgba(59,130,246,${1-dist/120})`;this.ctx.lineWidth=1;this.ctx.stroke()}})}}class Particle{constructor(w,h){this.x=Math.random()*w;this.y=Math.random()*h;this.vx=(Math.random()-0.5)*2;this.vy=(Math.random()-0.5)*2;this.radius=Math.random()*3+1;this.color='#3b82f6'}update(mouse){if(mouse.x!==null){const dx=mouse.x-this.x;const dy=mouse.y-this.y;const dist=Math.sqrt(dx*dx+dy*dy);if(dist<150){this.vx-=dx*0.0005;this.vy-=dy*0.0005}}this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>canvas.width)this.vx*=-1;if(this.y<0||this.y>canvas.height)this.vy*=-1}draw(ctx){ctx.beginPath();ctx.arc(this.x,this.y,this.radius,0,Math.PI*2);ctx.fillStyle=this.color;ctx.fill()}}"
    },
]

FULLSTACK = [
    {
        "prompt": "Build a full-stack React + FastAPI note-taking app with CRUD and auth",
        "code": "// Frontend: React with fetch and auth context import React, { createContext, useContext, useState, useEffect } from 'react'; const AuthContext = createContext(null); export function AuthProvider({ children }) { const [user, setUser] = useState(null); const [token, setToken] = useState(localStorage.getItem('token')); const login = async (email, password) => { const res = await fetch('/api/auth/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) }); if (!res.ok) throw new Error('Login failed'); const data = await res.json(); localStorage.setItem('token', data.token); setToken(data.token); setUser(data.user); }; const logout = () => { localStorage.removeItem('token'); setToken(null); setUser(null); }; return <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>; } export function useAuth() { return useContext(AuthContext); } function NotesApp() { const { token } = useAuth(); const [notes, setNotes] = useState([]); const [loading, setLoading] = useState(true); useEffect(() => { if (!token) { setLoading(false); return; } fetch('/api/notes', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json()).then(data => { setNotes(data.notes); setLoading(false); }).catch(() => setLoading(false)); }, [token]); const createNote = async (title, content) => { const res = await fetch('/api/notes', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }, body: JSON.stringify({ title, content }) }); if (res.ok) { const note = await res.json(); setNotes(prev => [note, ...prev]); } }; const deleteNote = async (id) => { const res = await fetch(`/api/notes/${id}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } }); if (res.ok) setNotes(prev => prev.filter(n => n.id !== id)); }; if (loading) return <div className='spinner'/>; return (<div className='notes-app'><div className='notes-grid'>{notes.map(note => (<div key={note.id} className='note-card'><h3>{note.title}</h3><p>{note.content}</p><button onClick={() => deleteNote(note.id)}>Delete</button></div>))}</div></div>); }\n// Backend: FastAPI notes endpoint with JWT auth from fastapi import FastAPI, Depends, HTTPException from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials from jose import JWTError, jwt import databases security = HTTPBearer() app = FastAPI() async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)): try: payload = jwt.decode(credentials.credentials, 'secret', algorithms=['HS256']) return payload['sub'] except JWTError: raise HTTPException(401, 'Invalid token') @app.get('/api/notes') async def list_notes(user_id: int = Depends(get_current_user)): query = 'SELECT id, title, content, created_at FROM notes WHERE user_id = :uid ORDER BY created_at DESC' notes = await database.fetch_all(query=query, values={'uid': user_id}) return {'notes': [dict(n) for n in notes]} @app.post('/api/notes') async def create_note(data: dict, user_id: int = Depends(get_current_user)): title = data.get('title', 'Untitled')[:200] content = data.get('content', '')[:5000] query = 'INSERT INTO notes (user_id, title, content) VALUES (:uid, :title, :content) RETURNING id' note_id = await database.execute(query=query, values={'uid': user_id, 'title': title, 'content': content}) return {'id': note_id, 'title': title, 'content': content, 'user_id': user_id} @app.delete('/api/notes/{note_id}') async def delete_note(note_id: int, user_id: int = Depends(get_current_user)): query = 'DELETE FROM notes WHERE id = :nid AND user_id = :uid' deleted = await database.execute(query=query, values={'nid': note_id, 'uid': user_id}) if not deleted: raise HTTPException(404, 'Note not found') return {'deleted': True}"
    },
    {
        "prompt": "Implement a full-stack real-time chat app with WebSocket and React",
        "code": "// Frontend: WebSocket chat hook import { useState, useEffect, useRef, useCallback } from 'react'; function useWebSocket(url) { const [messages, setMessages] = useState([]); const [connected, setConnected] = useState(false); const ws = useRef(null); const reconnectTimeout = useRef(null); const connect = useCallback(() => { if (ws.current?.readyState === WebSocket.OPEN) return; ws.current = new WebSocket(url); ws.current.onopen = () => setConnected(true); ws.current.onmessage = (event) => { const msg = JSON.parse(event.data); setMessages(prev => [...prev, msg]); }; ws.current.onclose = () => { setConnected(false); reconnectTimeout.current = setTimeout(connect, 3000); }; ws.current.onerror = () => ws.current?.close(); }, [url]); useEffect(() => { connect(); return () => { clearTimeout(reconnectTimeout.current); ws.current?.close(); }; }, [connect]); const send = useCallback((data) => { if (ws.current?.readyState === WebSocket.OPEN) { ws.current.send(JSON.stringify(data)); } }, []); return { messages, connected, send }; }\n// Backend: FastAPI WebSocket handler with room management from fastapi import FastAPI, WebSocket, WebSocketDisconnect from typing import Set import json app = FastAPI() class ConnectionManager: def __init__(self): self.rooms: dict[str, Set[WebSocket]] = {} async def connect(self, websocket: WebSocket, room: str): await websocket.accept() if room not in self.rooms: self.rooms[room] = set() self.rooms[room].add(websocket) async def disconnect(self, websocket: WebSocket, room: str): self.rooms[room].discard(websocket) if not self.rooms[room]: del self.rooms[room] async def broadcast(self, message: dict, room: str): if room not in self.rooms: return dead = set() for ws in self.rooms[room]: try: await ws.send_json(message) except: dead.add(ws) self.rooms[room] -= dead manager = ConnectionManager() @app.websocket('/ws/{room_id}') async def chat_websocket(websocket: WebSocket, room_id: str): await manager.connect(websocket, room_id) try: while True: data = await websocket.receive_json() data['type'] = 'message' await manager.broadcast(data, room_id) except WebSocketDisconnect: await manager.disconnect(websocket, room_id)"
    },
]

DEBUG_COMMON = [
    {
        "prompt": "Fix CORS error when frontend fetches from a different origin",
        "code_before": "fetch('https://api.example.com/data').then(r => r.json()).then(console.log).catch(console.error)",
        "code_after": "// CORS error: browser blocks cross-origin requests without proper headers\n// Fix backend: add CORS middleware\n// from fastapi.middleware.cors import CORSMiddleware\n// app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:3000'], allow_methods=['*'], allow_headers=['*'])\n// For dev, use: mode: 'cors' in fetch options\nfetch('https://api.example.com/data', { mode: 'cors', credentials: 'include' }).then(r => r.json()).then(console.log).catch(console.error)",
        "error_type": "CORS"
    },
    {
        "prompt": "Fix React useEffect infinite loop from missing dependency array",
        "code_before": "useEffect(() => { fetchData().then(setData); });",
        "code_after": "// Infinite loop: useEffect runs after every render without deps\n// Fix: add empty dep array for mount-only, or list dependencies\nuseEffect(() => { fetchData().then(setData); }, []);",
        "error_type": "react-effect"
    },
    {
        "prompt": "Fix null reference error when accessing nested object property",
        "code_before": "const userName = user.profile.name;",
        "code_after": "// TypeError: Cannot read property 'name' of undefined\n// Fix: optional chaining with fallback\nconst userName = user?.profile?.name ?? 'Anonymous';",
        "error_type": "null-reference"
    },
    {
        "prompt": "Fix async race condition where state is read before it updates",
        "code_before": "let data = []; fetch('/api/data').then(r => r.json()).then(d => data = d); console.log(data.length);",
        "code_after": "// Race: console.log runs before fetch completes\n// Fix: chain properly with async/await\nasync function loadData() { const response = await fetch('/api/data'); const data = await response.json(); console.log(data.length); return data; }",
        "error_type": "async-race"
    },
    {
        "prompt": "Fix memory leak from setInterval not being cleared in React component",
        "code_before": "useEffect(() => { setInterval(() => { setTime(new Date()); }, 1000); }, []);",
        "code_after": "// Memory leak: interval continues after unmount\n// Fix: store and clear in cleanup function\nuseEffect(() => { const timer = setInterval(() => { setTime(new Date()); }, 1000); return () => clearInterval(timer); }, []);",
        "error_type": "memory-leak"
    },
    {
        "prompt": "Fix SQL injection vulnerability in raw query string interpolation",
        "code_before": "query = f\"SELECT * FROM users WHERE email = '{email}'\"",
        "code_after": "// SQL injection: attacker can inject ' OR 1=1 --\n// Fix: use parameterized query\nquery = 'SELECT * FROM users WHERE email = :email'\nresult = await database.fetch_all(query=query, values={'email': email})",
        "error_type": "security"
    },
    {
        "prompt": "Fix XSS vulnerability from directly setting innerHTML with user input",
        "code_before": "element.innerHTML = userInput;",
        "code_after": "// XSS: user can inject <script>alert('xss')</script>\n// Fix: use textContent for text, or sanitize with DOMPurify\nimport DOMPurify from 'dompurify';\nelement.innerHTML = DOMPurify.sanitize(userInput);\n// Even better: use textContent when no HTML needed\nelement.textContent = userInput;",
        "error_type": "security"
    },
]

NLP_INTENT = [
    {
        "prompt": "Build me a React todo app",
        "intent": "build", "mode": "build", "domain": "frontend",
        "response": "Building a React todo app with add, toggle, and delete. Starting component scaffold..."
    },
    {
        "prompt": "How do I fix this CORS error?",
        "intent": "debug", "mode": "build", "domain": "debug",
        "response": "CORS errors happen when frontend origin doesn't match API origin. Add CORS middleware to your backend."
    },
    {
        "prompt": "Explain how CSS Grid works",
        "intent": "chat", "mode": "plan", "domain": "design",
        "response": "CSS Grid is a 2D layout system. Use display: grid on the container, then grid-template-columns and grid-template-rows to define tracks."
    },
]

def generate_frontend_html(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"frontend_html_{i}".encode()).hexdigest())
        example = rng.choice(FRONTEND_HTML)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "frontend"})
    return data

def generate_frontend_css(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"frontend_css_{i}".encode()).hexdigest())
        example = rng.choice(FRONTEND_CSS)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "frontend"})
    return data

def generate_frontend_js(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"frontend_js_{i}".encode()).hexdigest())
        example = rng.choice(FRONTEND_JS)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "frontend"})
    return data

def generate_frontend_react(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"frontend_react_{i}".encode()).hexdigest())
        example = rng.choice(FRONTEND_REACT)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "frontend"})
    return data

def generate_backend_python(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"backend_python_{i}".encode()).hexdigest())
        example = rng.choice(BACKEND_PYTHON)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "backend"})
    return data

def generate_backend_api(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"backend_api_{i}".encode()).hexdigest())
        example = rng.choice(BACKEND_API)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "backend"})
    return data

def generate_design_layout(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"design_layout_{i}".encode()).hexdigest())
        example = rng.choice(DESIGN_LAYOUT)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "design"})
    return data

def generate_design_animation(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"design_animation_{i}".encode()).hexdigest())
        example = rng.choice(DESIGN_ANIMATION)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "design"})
    return data

def generate_fullstack(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"fullstack_{i}".encode()).hexdigest())
        example = rng.choice(FULLSTACK)
        prompt_tokens = tokenize(example["prompt"])
        code_tokens = tokenize(example["code"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [5] + code_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "fullstack"})
    return data

def generate_debug(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"debug_{i}".encode()).hexdigest())
        example = rng.choice(DEBUG_COMMON)
        prompt_tokens = tokenize(example["prompt"])
        before_tokens = tokenize(example["code_before"])
        after_tokens = tokenize(example["code_after"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14] + before_tokens + [14]
        target_ids = [6] + after_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": "build", "domain": "debug"})
    return data

def generate_nlp(n):
    data = []
    for i in range(n):
        rng = random.Random(hashlib.md5(f"nlp_{i}".encode()).hexdigest())
        example = rng.choice(NLP_INTENT)
        prompt_tokens = tokenize(example["prompt"])
        response_tokens = tokenize(example["response"])
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [4] + response_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:512], "mode": example["mode"], "domain": "nlp"})
    return data

def generate_plan_examples(n, domain):
    data = []
    domains_plans = {
        "frontend": [
            "Plan the component hierarchy first, then style with CSS modules, finally add interaction logic",
            "Start with HTML skeleton, establish CSS layout with flexbox, then enhance with JavaScript event handlers",
            "I'll structure this as a parent component with child components for each section, using props for data flow",
        ],
        "backend": [
            "Design the database schema first, create API endpoints, then implement business logic with error handling",
            "Set up the project with dependency injection pattern, define data models, then implement service layer",
            "Use repository pattern for data access, service layer for business logic, and DTOs for API contracts",
        ],
        "design": [
            "Apply mobile-first responsive design, using CSS Grid for layout and custom properties for theming",
            "Establish design tokens first (colors, spacing, typography), then build component styles from those tokens",
            "Create wireframe, then high-fidelity mockup, then implement with HTML/CSS with attention to accessibility",
        ],
        "fullstack": [
            "Define API contract first, implement backend endpoints, then build frontend components that consume the API",
            "Set up database schema with migrations, implement auth flow, create protected routes, then connect frontend",
            "Start with data model, build API with validation, implement state management on frontend, handle errors end-to-end",
        ],
        "debug": [
            "Reproduce the error first, isolate the root cause using debugger, then apply fix and verify with tests",
            "Check error logs, narrow down to specific function, write a minimal reproduction, then implement the fix",
        ],
    }
    plans = domains_plans.get(domain, domains_plans["frontend"])
    topics = {
        "frontend": ["Build responsive navbar", "Create user profile card", "Implement image gallery"],
        "backend": ["Create user CRUD API", "Build search endpoint", "Implement file upload service"],
        "design": ["Design landing page hero", "Build pricing table", "Create dashboard layout"],
        "fullstack": ["Build auth login flow", "Create comment system", "Implement search feature"],
        "debug": ["Fix memory leak", "Resolve race condition", "Patch XSS vulnerability"],
    }
    topics_list = topics.get(domain, topics["frontend"])
    for i in range(n):
        rng = random.Random(hashlib.md5(f"plan_{domain}_{i}".encode()).hexdigest())
        topic = rng.choice(topics_list)
        plan = rng.choice(plans)
        prompt_tokens = tokenize(f"How should I {topic}?")
        plan_tokens = tokenize(plan)
        input_ids = [SPECIAL['BOS']] + prompt_tokens + [14]
        target_ids = [4] + plan_tokens + [1]
        data.append({"input_ids": input_ids[:256], "target_ids": target_ids[:384], "mode": "plan", "domain": domain})
    return data

def save_jsonl(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def generate_all(output_dir="data/advanced"):
    total = 0
    all_data = []

    generators = [
        ("frontend_html", generate_frontend_html, 8000),
        ("frontend_css", generate_frontend_css, 8000),
        ("frontend_js", generate_frontend_js, 8000),
        ("frontend_react", generate_frontend_react, 8000),
        ("frontend_plan", lambda n: generate_plan_examples(n, "frontend"), 8000),
        ("backend_python", generate_backend_python, 10000),
        ("backend_api", generate_backend_api, 10000),
        ("backend_plan", lambda n: generate_plan_examples(n, "backend"), 8000),
        ("design_layout", generate_design_layout, 8000),
        ("design_animation", generate_design_animation, 8000),
        ("design_plan", lambda n: generate_plan_examples(n, "design"), 4000),
        ("fullstack", generate_fullstack, 15000),
        ("fullstack_plan", lambda n: generate_plan_examples(n, "fullstack"), 5000),
        ("debug", generate_debug, 20000),
        ("debug_plan", lambda n: generate_plan_examples(n, "debug"), 5000),
        ("nlp", generate_nlp, 5000),
    ]

    print("Generating advanced training data...")
    for name, gen_fn, count in generators:
        print(f"  {name}: {count} examples...")
        data = gen_fn(count)
        save_jsonl(data, f"{output_dir}/{name}.jsonl")
        all_data.extend(data)
        total += len(data)
        print(f"    -> {len(data)} generated")

    rng = random.Random(42)
    rng.shuffle(all_data)

    split = int(len(all_data) * 0.9)
    train = all_data[:split]
    val = all_data[split:]

    save_jsonl(train, f"{output_dir}/train.jsonl")
    save_jsonl(val, f"{output_dir}/val.jsonl")
    print(f"\nTotal: {len(all_data)} (train: {len(train)}, val: {len(val)})")

    domain_counts = {}
    for item in all_data:
        d = item.get("domain", "unknown")
        domain_counts[d] = domain_counts.get(d, 0) + 1
    print("Domain breakdown:")
    for d, c in sorted(domain_counts.items()):
        print(f"  {d}: {c}")
    print("Done.")


if __name__ == '__main__':
    generate_all()
