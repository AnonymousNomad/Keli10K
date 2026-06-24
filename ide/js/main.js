(function () {
'use strict';

const DB_NAME = 'snca-ide';
const STORE = 'files';
let editor, db, currentFile = 'untitled', fileTree = {};
let mode = 'plan';

const $ = id => document.getElementById(id);
const terminal = $('terminal-output');
const chatMessages = $('chat-messages');
const chatInput = $('chat-input');
const fileTreeEl = $('file-tree');
const filenameDisplay = $('filename-display');
const buildOutput = $('build-output');
const buildFrame = $('build-frame');

function log(msg, cls) {
  const d = document.createElement('div');
  d.className = 'term-' + (cls || 'log');
  d.textContent = '> ' + msg;
  terminal.appendChild(d);
  terminal.scrollTop = terminal.scrollHeight;
}

function openDB() {
  return new Promise((resolve, reject) => {
    const r = indexedDB.open(DB_NAME, 1);
    r.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE)) {
        const s = db.createObjectStore(STORE, { keyPath: 'name' });
        s.put({ name: 'untitled', content: '', language: 'javascript' });
      }
    };
    r.onsuccess = e => resolve(e.target.result);
    r.onerror = e => reject(e.target.error);
  });
}

async function loadFiles() {
  const tx = db.transaction(STORE, 'readonly');
  const store = tx.objectStore(STORE);
  const all = await new Promise(r => { const req = store.getAll(); req.onsuccess = () => r(req.result); });
  fileTree = {};
  all.forEach(f => fileTree[f.name] = f);
  renderFileTree();
}

async function saveFile(name, content, lang) {
  const tx = db.transaction(STORE, 'readwrite');
  tx.objectStore(STORE).put({ name, content, language: lang || 'javascript' });
  fileTree[name] = { name, content, language: lang || 'javascript' };
  renderFileTree();
}

async function deleteFile(name) {
  if (name === 'untitled') return;
  const tx = db.transaction(STORE, 'readwrite');
  tx.objectStore(STORE).delete(name);
  delete fileTree[name];
  if (currentFile === name) {
    currentFile = 'untitled';
    filenameDisplay.textContent = 'untitled';
    editor.setValue(fileTree['untitled']?.content || '');
  }
  renderFileTree();
}

function renderFileTree() {
  const names = Object.keys(fileTree).sort();
  fileTreeEl.innerHTML = names.map(n => {
    const ext = n.split('.').pop();
    const icon = ({ js: '\u{1F7E8}', jsx: '\u{1F7E8}', py: '\u{1F7E9}', css: '\u{1F7E6}', html: '\u{1F7E7}' })[ext] || '\u{1F7E5}';
    const active = n === currentFile ? ' active' : '';
    return `<div class="file-item${active}" data-file="${n}"><span class="icon">${icon}</span><span class="name">${n}</span><button class="del-btn" data-file="${n}">\u2715</button></div>`;
  }).join('');
  fileTreeEl.querySelectorAll('.file-item').forEach(el => el.addEventListener('click', e => { if (!e.target.closest('.del-btn')) openFile(el.dataset.file); }));
  fileTreeEl.querySelectorAll('.del-btn').forEach(el => el.addEventListener('click', e => { e.stopPropagation(); deleteFile(el.dataset.file); }));
}

async function openFile(name) {
  const f = fileTree[name];
  if (!f) return;
  currentFile = name;
  filenameDisplay.textContent = name;
  editor.setValue(f.content || '');
  editor.focus();
  renderFileTree();
  const mm = { js: 'javascript', jsx: 'javascript', py: 'python', css: 'css', html: 'htmlmixed', json: 'javascript' };
  editor.setOption('mode', mm[name.split('.').pop()] || 'javascript');
}

async function newFile() {
  const name = prompt('File name:', 'script.js');
  if (!name || fileTree[name]) return;
  const lm = { js: 'javascript', jsx: 'javascript', py: 'python', css: 'css', html: 'htmlmixed', json: 'javascript' };
  await saveFile(name, '', lm[name.split('.').pop()] || 'javascript');
  await openFile(name);
}

function addThinkingBubble() {
  const d = document.createElement('div');
  d.className = 'msg keli';
  d.id = 'thinking-bubble';
  d.innerHTML = '<div class="msg-bubble thinking">Keli is thinking...</div>';
  chatMessages.appendChild(d);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeThinkingBubble() {
  const tb = document.getElementById('thinking-bubble');
  if (tb) tb.remove();
}

function addChatMessage(text, isUser, citations) {
  const d = document.createElement('div');
  d.className = 'msg ' + (isUser ? 'user' : 'keli');
  let html = '<div class="msg-bubble">' + escapeHtml(text) + '</div>';
  if (citations && citations.length > 0) {
    html += '<div class="msg-citations">' + citations.map(c => '<a href="#" class="cite-link">' + escapeHtml(c) + '</a>').join(', ') + '</div>';
  }
  d.innerHTML = html;
  chatMessages.appendChild(d);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(t) {
  const d = document.createElement('div');
  d.textContent = t;
  return d.innerHTML;
}

async function handleChat() {
  const text = chatInput.value.trim();
  if (!text) return;
  chatInput.value = '';
  addChatMessage(text, true);
  addThinkingBubble();
  log('Keli processing: "' + text.slice(0, 40) + (text.length > 40 ? '..."' : '"'), 'info');

  // Check for tutor mode
  if (text.toLowerCase().includes('teach me') || text.toLowerCase().includes('learn')) {
    const task = text.replace(/teach me (to |how to )?/i, '').trim();
    if (window.KeliTutor && window.KeliTutor.loadLesson(task)) {
      removeThinkingBubble();
      addChatMessage(`Alright dumbass. Let's build a ${task}. Opening the lesson panel.`, false);
      log('Tutor mode activated: ' + task, 'success');
      if (window.KeliAudio) window.KeliAudio.setState('tutor');
      return;
    }
  }

  try {
    const data = await api.chat(text);
    removeThinkingBubble();
    const reply = data.response || data.synthesis || 'I got nothing, dumbass.';
    addChatMessage(reply, false, data.citations);
    log('Keli response received', 'success');
    if (data.mode === 'build') {
      document.getElementById('mode-toggle').textContent = 'Build';
      mode = 'build';
    }
  } catch (e) {
    removeThinkingBubble();
    const errMsg = api.getUserError(e);
    addChatMessage(errMsg, false);
    log('Chat error: ' + (e.message || 'unknown'), 'error');
    handleOfflineChat(text);
  }
}

function handleOfflineChat(text) {
  const lower = text.toLowerCase();
  if (lower.includes('build') || lower.includes('create') || lower.includes('make')) {
    const fallback = 'function ' + (text.match(/\w+/) || ['App'])[0] + '() {\n  // TODO: implement\n  return null;\n}';
    editor.setValue(fallback);
    addChatMessage('Offline mode. Stub generated.', false);
  } else if (lower.includes('hello') || lower.includes('hi')) {
    addChatMessage('Hey dumbass. What do you want?', false);
  } else {
    addChatMessage('I am in offline mode and my nanobots are taking a nap.', false);
  }
}

async function handleBuild() {
  const code = editor.getValue();
  const fileName = currentFile;
  log('Building: ' + fileName, 'build');
  addThinkingBubble();
  if (window.KeliAudio) window.KeliAudio.setState('building');

  try {
    const files = {};
    Object.keys(fileTree).forEach(k => { files[k] = fileTree[k].content; });
    if (!files[fileName]) files[fileName] = code;

    const data = await api.build('Build ' + fileName, files);
    removeThinkingBubble();

    if (data.files) {
      for (const [fname, fcontent] of Object.entries(data.files)) {
        await saveFile(fname, fcontent);
      }
      log('Territories: ' + (data.territories || []).join(', '), 'success');
      addChatMessage('Built: ' + Object.keys(data.files).join(', '), false);

      if (Object.keys(data.files).length > 0) {
        const firstFile = Object.keys(data.files)[0];
        await openFile(firstFile);
      }

      if (window.KeliAudio) window.KeliAudio.setState('success');
      if (window.KeliBlueprint) window.KeliBlueprint.pulseAll();
    } else {
      addChatMessage('Build returned nothing.', false);
    }

    if (data.error) log('Build error: ' + data.error, 'error');
  } catch (e) {
    removeThinkingBubble();
    const errMsg = api.getUserError(e);
    addChatMessage(errMsg, false);
    log('Build failed: ' + (e.message || 'unknown'), 'error');
    if (window.KeliAudio) window.KeliAudio.setState('error');
    handleLocalBuild(code, fileName);
  }
}

function handleLocalBuild(code, fileName) {
  const ext = fileName.split('.').pop();
  if (ext === 'html') {
    buildFrame.src = 'data:text/html;charset=utf-8,' + encodeURIComponent(code);
    buildOutput.classList.remove('hidden');
    log('Local HTML preview', 'success');
  } else if (ext === 'js' || ext === 'jsx') {
    const html = '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body><div id="root"></div><script>' + code + '\n<\/script></body></html>';
    buildFrame.src = 'data:text/html;charset=utf-8,' + encodeURIComponent(html);
    buildOutput.classList.remove('hidden');
    log('Local JS preview', 'success');
  } else {
    log('No local preview for .' + ext, 'warn');
  }
}

async function handleRun() {
  const code = editor.getValue();
  const files = {};
  Object.keys(fileTree).forEach(k => { files[k] = fileTree[k].content; });
  log('Running preview...', 'info');

  try {
    const data = await api.preview(files);
    if (data.rendered_html) {
      buildFrame.src = 'data:text/html;charset=utf-8,' + encodeURIComponent(data.rendered_html);
      buildOutput.classList.remove('hidden');
      log('Preview rendered', 'success');
    }
    if (data.console_output && data.console_output.length > 0) {
      data.console_output.forEach(l => log('[console] ' + l, 'info'));
    }
    if (data.errors && data.errors.length > 0) {
      data.errors.forEach(e => log('Preview error: ' + e, 'error'));
    }
  } catch (e) {
    log('Preview unavailable: ' + api.getUserError(e), 'warn');
    handleLocalBuild(code, currentFile);
  }
}

async function handleExport() {
  const files = {};
  Object.keys(fileTree).forEach(k => { files[k] = fileTree[k].content; });
  if (Object.keys(files).length === 0) {
    log('Nothing to export', 'warn');
    return;
  }
  log('Packaging ' + Object.keys(files).length + ' files...', 'info');
  addThinkingBubble();

  try {
    const data = await api.export(files, 'static');
    removeThinkingBubble();
    log('Shipped to ' + (data.zip_path || 'export'), 'success');
    if (data.download_url) {
      const urlPart = data.download_url.replace('/download/', '');
      await api.download(urlPart);
      log('Download started', 'success');
    }
  } catch (e) {
    removeThinkingBubble();
    log('Export failed: ' + api.getUserError(e), 'error');
  }
}

async function handleShipIt() {
  await handleExport();
}

async function handleSave() {
  const content = editor.getValue();
  await saveFile(currentFile, content, editor.getMode().name);
  log('Saved: ' + currentFile, 'success');
}

class AlaskaFusionCanvas {
  constructor() {
    this.water = $('water-canvas');
    this.underwater = $('underwater-canvas');
    this.fishCanvas = $('fish-canvas');
    this.ctx = [this.water.getContext('2d'), this.underwater.getContext('2d'), this.fishCanvas.getContext('2d')];
    this.fish = [];
    this.snow = [];
    this.bubbles = [];
    this.binaryColumns = [];
    this.auroraPhase = 0;
    this.time = 0;
    this.mouseX = 0;
    this.mouseY = 0;
    this.resize();
    window.addEventListener('resize', () => this.resize());
    document.addEventListener('mousemove', e => { this.mouseX = e.clientX; this.mouseY = e.clientY; });
    for (let i = 0; i < 8; i++) {
      this.fish.push({
        x: Math.random() * this.w, y: Math.random() * this.h * 0.7 + this.h * 0.3,
        vx: (Math.random() - 0.5) * 1.5, vy: (Math.random() - 0.5) * 0.3,
        len: 15 + Math.random() * 20, phase: Math.random() * Math.PI * 2,
      });
    }
    for (let i = 0; i < 50; i++) {
      this.snow.push({ x: Math.random() * this.w, y: Math.random() * this.h, size: 1 + Math.random() * 3, speed: 0.3 + Math.random() * 0.5, drift: (Math.random() - 0.5) * 0.3 });
    }
    for (let i = 0; i < 30; i++) {
      this.bubbles.push({ x: Math.random() * this.w, y: Math.random() * this.h, r: 2 + Math.random() * 6, speed: 0.2 + Math.random() * 0.4 });
    }
    for (let i = 0; i < 15; i++) {
      this.binaryColumns.push({ x: Math.random() * this.w, speed: 0.5 + Math.random() * 1, chars: [] });
    }
    this.animate();
  }
  resize() {
    this.w = window.innerWidth; this.h = window.innerHeight;
    [this.water, this.underwater, this.fishCanvas].forEach(c => { c.width = this.w; c.height = this.h; });
  }
  animate() {
    this.time += 0.016;
    this.drawGlacialDepths();
    this.drawAurora();
    this.drawBinaryRain();
    this.drawSnow();
    this.drawBubbles();
    this.drawFish();
    this.drawIceCrystals();
    requestAnimationFrame(() => this.animate());
  }
  drawGlacialDepths() {
    const c = this.ctx[0];
    c.clearRect(0, 0, this.w, this.h);
    // Deep glacial gradient
    const g = c.createRadialGradient(this.w * 0.5, this.h * 0.3, 0, this.w * 0.5, this.h * 0.5, this.h * 0.8);
    g.addColorStop(0, 'rgba(10, 22, 40, 0.6)');
    g.addColorStop(0.5, 'rgba(5, 12, 24, 0.8)');
    g.addColorStop(1, 'rgba(2, 6, 12, 0.95)');
    c.fillStyle = g;
    c.fillRect(0, 0, this.w, this.h);
    // Caustics
    for (let i = 0; i < 6; i++) {
      c.strokeStyle = `rgba(0, 229, 255, ${0.03 + Math.sin(this.time + i * 1.5) * 0.02})`;
      c.lineWidth = 0.5;
      c.beginPath();
      for (let x = 0; x < this.w; x += 4) {
        const y = this.h * 0.2 + Math.sin(x * 0.008 + this.time * 0.5 + i) * 15 + Math.sin(x * 0.015 + this.time + i * 2) * 8;
        x === 0 ? c.moveTo(x, y) : c.lineTo(x, y);
      }
      c.stroke();
    }
  }
  drawAurora() {
    const c = this.ctx[0];
    this.auroraPhase += 0.003;
    const auroraY = this.h * 0.15;
    for (let i = 0; i < 5; i++) {
      const alpha = 0.04 + Math.sin(this.auroraPhase + i * 1.2) * 0.03;
      c.fillStyle = i % 2 === 0 ? `rgba(0, 229, 255, ${alpha})` : `rgba(185, 103, 255, ${alpha})`;
      c.beginPath();
      c.moveTo(0, auroraY + i * 15);
      for (let x = 0; x < this.w; x += 10) {
        const y = auroraY + i * 15 + Math.sin(x * 0.003 + this.auroraPhase * 2 + i * 0.7) * 40 + Math.sin(x * 0.007 + this.auroraPhase + i * 1.3) * 20;
        c.lineTo(x, y);
      }
      c.lineTo(this.w, auroraY + 100 + i * 15);
      c.lineTo(0, auroraY + 100 + i * 15);
      c.closePath();
      c.fill();
    }
  }
  drawBinaryRain() {
    const c = this.ctx[0];
    this.binaryColumns.forEach(col => {
      col.y = (col.y || 0) + col.speed;
      if (col.y > this.h) { col.y = -20; col.x = Math.random() * this.w; }
      for (let i = 0; i < 8; i++) {
        const ch = Math.random() > 0.5 ? '0' : '1';
        const alpha = 0.06 * (1 - i / 8);
        c.fillStyle = `rgba(0, 229, 255, ${alpha})`;
        c.font = '10px monospace';
        c.fillText(ch, col.x, col.y - i * 14);
      }
    });
  }
  drawSnow() {
    const c = this.ctx[1];
    c.clearRect(0, 0, this.w, this.h);
    this.snow.forEach(s => {
      s.y += s.speed;
      s.x += s.drift + Math.sin(this.time + s.y * 0.01) * 0.2;
      if (s.y > this.h) { s.y = -5; s.x = Math.random() * this.w; }
      c.fillStyle = `rgba(192, 214, 228, ${0.3 + Math.sin(this.time * 2 + s.x) * 0.15})`;
      c.beginPath();
      c.arc(s.x, s.y, s.size, 0, Math.PI * 2);
      c.fill();
    });
  }
  drawBubbles() {
    const c = this.ctx[1];
    this.bubbles.forEach(b => {
      b.y -= b.speed;
      b.x += Math.sin(this.time + b.y * 0.1) * 0.2;
      if (b.y < -10) { b.y = this.h + 10; b.x = Math.random() * this.w; }
      c.strokeStyle = `rgba(0, 229, 255, ${0.08 + Math.sin(this.time + b.x) * 0.04})`;
      c.lineWidth = 0.5;
      c.beginPath();
      c.arc(b.x, b.y, b.r, 0, Math.PI * 2);
      c.stroke();
    });
  }
  drawFish() {
    const c = this.ctx[2];
    c.clearRect(0, 0, this.w, this.h);
    this.fish.forEach(f => {
      f.vx += (Math.random() - 0.5) * 0.03;
      f.vy += Math.sin(this.time * 0.5 + f.x * 0.02) * 0.005;
      f.vx = Math.max(-1.5, Math.min(1.5, f.vx));
      f.vy = Math.max(-0.4, Math.min(0.4, f.vy));
      f.x += f.vx;
      f.y += f.vy;
      if (f.x < -30) f.x = this.w + 20;
      if (f.x > this.w + 30) f.x = -20;
      if (f.y < this.h * 0.2) f.vy = 0.2;
      if (f.y > this.h * 0.9) f.vy = -0.2;
      const angle = Math.atan2(f.vy, f.vx);
      c.save();
      c.translate(f.x, f.y);
      c.rotate(angle);
      // Fish body - silvery
      const grad = c.createLinearGradient(-f.len * 0.5, 0, f.len * 0.5, 0);
      grad.addColorStop(0, 'rgba(150, 180, 200, 0.4)');
      grad.addColorStop(0.5, 'rgba(192, 214, 228, 0.6)');
      grad.addColorStop(1, 'rgba(150, 180, 200, 0.3)');
      c.fillStyle = grad;
      c.beginPath();
      c.ellipse(0, 0, f.len * 0.5, f.len * 0.15, 0, 0, Math.PI * 2);
      c.fill();
      // HUD marker (fusion element)
      c.fillStyle = `rgba(0, 229, 255, ${0.3 + Math.sin(this.time * 2 + f.x) * 0.2})`;
      c.beginPath();
      c.arc(f.len * 0.2, -2, 2, 0, Math.PI * 2);
      c.fill();
      c.restore();
    });
  }
  drawIceCrystals() {
    const c = this.ctx[1];
    for (let i = 0; i < 5; i++) {
      const x = (i / 5) * this.w + Math.sin(this.time * 0.3 + i) * 20;
      const y = this.h * 0.5 + Math.sin(this.time * 0.2 + i * 2) * 60;
      const size = 20 + Math.sin(this.time * 0.5 + i) * 8;
      c.strokeStyle = `rgba(0, 229, 255, ${0.04 + Math.sin(this.time + i) * 0.03})`;
      c.lineWidth = 1;
      // Hexagonal crystal
      for (let j = 0; j < 6; j++) {
        const a1 = (j / 6) * Math.PI * 2;
        const a2 = ((j + 1) / 6) * Math.PI * 2;
        c.beginPath();
        c.moveTo(x + Math.cos(a1) * size, y + Math.sin(a1) * size);
        c.lineTo(x + Math.cos(a2) * size, y + Math.sin(a2) * size);
        c.stroke();
      }
      // Inner lines
      c.beginPath();
      c.moveTo(x, y - size);
      c.lineTo(x, y + size);
      c.moveTo(x - size, y);
      c.lineTo(x + size, y);
      c.stroke();
    }
  }
}

function initCodemirror() {
  editor = CodeMirror.fromTextArea($('editor'), {
    theme: 'dracula', mode: 'javascript', lineNumbers: true,
    autoCloseBrackets: true, matchBrackets: true, indentUnit: 2, tabSize: 2,
    lineWrapping: false, viewportMargin: Infinity,
    extraKeys: { 'Ctrl-S': () => handleSave(), 'Cmd-S': () => handleSave(), 'Ctrl-Enter': () => handleRun(), 'Cmd-Enter': () => handleRun() },
  });
  editor.setValue('// Welcome to Keli — Arctic Fusion IDE\n// Chat with Keli or start coding.\n');
  editor.focus();
  // Typing detection for audio
  editor.on('change', () => {
    if (window.KeliAudio) window.KeliAudio.setState('typing');
    clearTimeout(window._typingTimer);
    window._typingTimer = setTimeout(() => {
      if (window.KeliAudio && !document.querySelector('.tutor-panel.active')) {
        window.KeliAudio.setState('idle');
      }
    }, 3000);
  });
}

async function healthPoll() {
  const status = document.getElementById('chat-status');
  try {
    const h = await api.health();
    status.textContent = h.status === 'ok' ? 'online' : 'offline';
    status.style.color = h.status === 'ok' ? '#00ffc8' : '#ff6b00';
  } catch {
    status.textContent = 'offline';
    status.style.color = '#ff6b00';
  }
}

async function checkSwarmStatus() {
  try {
    const resp = await fetch((API_BASE || '') + '/status');
    if (!resp.ok) throw new Error();
    const data = await resp.json();
    log(`Swarm: ${data.awake_bots}/${data.total_bots} bots | ${Object.entries(data.territory_balance).map(([k,v]) => k+':'+v+'%').join(' ')}`, 'success');
    if (window.KeliBlueprint) {
      window.KeliBlueprint.clearNodes();
      Object.entries(data.territory_balance).forEach(([k, v]) => {
        window.KeliBlueprint.addNode(k.toLowerCase(), k.toLowerCase(), Math.random() * 400 + 50, Math.random() * 300 + 50, k);
      });
      window.KeliBlueprint.render();
    }
  } catch {
    log('Swarm offline. Start api_server.py', 'warn');
  }
  healthPoll();
  setInterval(healthPoll, 30000);
}

document.addEventListener('DOMContentLoaded', async () => {
  initCodemirror();

  checkSwarmStatus();

  try {
    db = await openDB();
    await loadFiles();
    const f = fileTree['untitled'] || { name: 'untitled', content: '', language: 'javascript' };
    editor.setValue(f.content || '');
    currentFile = 'untitled';
    filenameDisplay.textContent = 'untitled';
    log('IndexedDB ready: ' + Object.keys(fileTree).length + ' files', 'success');
  } catch (e) {
    log('IndexedDB unavailable, using in-memory storage', 'warn');
    db = null;
  }

  // Initialize audio on first user interaction
  const initAudio = () => {
    if (window.KeliAudio) {
      window.KeliAudio.init();
      window.KeliAudio.setState('idle');
    }
    document.removeEventListener('click', initAudio);
    document.removeEventListener('keydown', initAudio);
  };
  document.addEventListener('click', initAudio);
  document.addEventListener('keydown', initAudio);

  // Initialize canvas
  new AlaskaFusionCanvas();

  // Initialize new modules
  if (window.KeliBlueprint) {
    window.KeliBlueprint.init('canvas-layer');
  }
  if (window.KeliTutor) {
    window.KeliTutor.init();
  }

  $('new-file-btn').addEventListener('click', newFile);
  $('save-btn').addEventListener('click', handleSave);
  $('build-btn').addEventListener('click', handleBuild);
  $('run-btn').addEventListener('click', handleRun);
  $('ship-btn').addEventListener('click', handleShipIt);
  $('build-close').addEventListener('click', () => buildOutput.classList.add('hidden'));
  $('terminal-clear').addEventListener('click', () => terminal.innerHTML = '');
  $('mode-toggle').addEventListener('click', () => {
    mode = mode === 'plan' ? 'build' : 'plan';
    $('mode-toggle').textContent = mode.charAt(0).toUpperCase() + mode.slice(1);
    log('Switched to ' + mode + ' mode', 'info');
  });
  $('chat-send').addEventListener('click', handleChat);
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleChat(); }
  });

  // Audio controls
  const audioContainer = document.createElement('div');
  audioContainer.className = 'audio-controls';
  audioContainer.innerHTML = `
    <button id="audio-mute">🔊</button>
    <input type="range" id="audio-volume" min="0" max="1" step="0.05" value="0.5">
  `;
  document.body.appendChild(audioContainer);
  $('#audio-volume').addEventListener('input', e => {
    if (window.KeliAudio) window.KeliAudio.setVolume(parseFloat(e.target.value));
  });
  $('#audio-mute').addEventListener('click', () => {
    if (window.KeliAudio) {
      if (window.KeliAudio._muted) {
        window.KeliAudio.unmute();
        $('#audio-mute').textContent = '🔊';
        window.KeliAudio._muted = false;
      } else {
        window.KeliAudio.mute();
        $('#audio-mute').textContent = '🔇';
        window.KeliAudio._muted = true;
      }
    }
  });

  setInterval(healthPoll, 5000);
  healthPoll();

  log('Keli Arctic Fusion IDE initialized. Mode: ' + mode, 'success');
  log('Build, code, and chat with Keli', 'info');
});

})();
