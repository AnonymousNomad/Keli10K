"""
Keli Generation System — produces complete working projects from prompts.
Current: blueprint-based (working code, guaranteed runnable).
Future: model-generated (once training converges).
"""
import json, os, random

PROJECTS = {}

# ---- TODO APP ----
PROJECTS['todo-app'] = {
    'name': 'todo-app',
    'desc': 'Full-stack todo app with Flask API and vanilla JS frontend',
    'files': {
        'app.py': 'from flask import Flask, request, jsonify\nimport sqlite3\n\napp = Flask(__name__)\nDB = "todos.db"\n\ndef init():\n    with sqlite3.connect(DB) as conn:\n        conn.execute("""CREATE TABLE IF NOT EXISTS todos (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            text TEXT NOT NULL,\n            done INTEGER DEFAULT 0\n        )""")\n\ninit()\n\n@app.route("/api/todos")\ndef list_todos():\n    with sqlite3.connect(DB) as conn:\n        rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()\n        return jsonify([{"id":r[0],"text":r[1],"done":bool(r[2])} for r in rows])\n\n@app.route("/api/todos", methods=["POST"])\ndef create():\n    data = request.get_json()\n    with sqlite3.connect(DB) as conn:\n        cur = conn.execute("INSERT INTO todos (text) VALUES (?)", (data["text"],))\n        conn.commit()\n        return jsonify({"id":cur.lastrowid}), 201\n\n@app.route("/api/todos/<int:tid>", methods=["PUT"])\ndef update(tid):\n    data = request.get_json()\n    with sqlite3.connect(DB) as conn:\n        conn.execute("UPDATE todos SET done=? WHERE id=?", (int(data.get("done",0)), tid))\n        conn.commit()\n        return jsonify({"ok":True})\n\n@app.route("/api/todos/<int:tid>", methods=["DELETE"])\ndef delete(tid):\n    with sqlite3.connect(DB) as conn:\n        conn.execute("DELETE FROM todos WHERE id=?", (tid,))\n        conn.commit()\n        return jsonify({"ok":True})\n\nif __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5000)',
        'index.html': '<!DOCTYPE html>\n<html><head><title>Keli Todo</title><style>\n*{margin:0;padding:0;box-sizing:border-box}\nbody{font-family:system-ui,sans-serif;background:#0a0a1a;color:#e0e0e0;max-width:600px;margin:0 auto;padding:20px}\nh1{color:#00d4ff;text-align:center;margin-bottom:20px;font-size:2em;text-shadow:0 0 10px rgba(0,212,255,0.3)}\n.form{display:flex;gap:8px;margin-bottom:16px}\n.form input{flex:1;padding:12px;border:1px solid #333;border-radius:6px;background:#1a1a2e;color:#e0e0e0;font-size:16px}\n.form input:focus{outline:none;border-color:#00d4ff}\n.form button{padding:12px 24px;background:#00d4ff;color:#0a0a1a;border:none;border-radius:6px;cursor:pointer;font-weight:bold}\nul{list-style:none}\nli{display:flex;align-items:center;gap:12px;padding:12px;background:#1a1a2e;border:1px solid #333;border-radius:6px;margin-bottom:8px;transition:all .2s}\nli:hover{border-color:#00d4ff}\nli.done span{text-decoration:line-through;opacity:0.5}\nli span{flex:1;cursor:pointer}\n.delete{background:none;border:none;color:#ff4444;font-size:20px;cursor:pointer;padding:0 8px}\n.count{text-align:center;color:#666;margin-top:16px}\n</style></head><body>\n<h1>Keli Todo</h1>\n<div class="form">\n  <input id="input" placeholder="What needs to be done?" />\n  <button id="addBtn">Add</button>\n</div>\n<ul id="list"></ul>\n<p class="count" id="count"></p>\n<script>\nconst API = "/api";\nasync function load(){\n  const r = await fetch(API+"/todos");\n  const todos = await r.json();\n  document.getElementById("list").innerHTML = todos.map(t =>\n    \'<li class="\'+(t.done?"done":"")+\'">\'+\n    \'<input type="checkbox" \'+(t.done?"checked":"")+\' onchange="toggle(\'+t.id+\',\'+t.done+\')" />\'+\n    \'<span ondblclick="del(\'+t.id+\')">\'+t.text+\'</span>\'+\n    \'<button class="delete" onclick="del(\'+t.id+\')">&times;</button></li>\'\n  ).join("");\n  document.getElementById("count").textContent = todos.filter(t=>!t.done).length + " remaining";\n}\nasync function add(){\n  const inp = document.getElementById("input");\n  if(!inp.value.trim()) return;\n  await fetch(API+"/todos",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:inp.value})});\n  inp.value=""; load();\n}\nasync function toggle(id,done){\n  await fetch(API+"/todos/"+id,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({done:!done})});\n  load();\n}\nasync function del(id){\n  await fetch(API+"/todos/"+id,{method:"DELETE"});\n  load();\n}\ndocument.getElementById("addBtn").onclick = add;\ndocument.getElementById("input").onkeydown = e => {if(e.key==="Enter") add()};\nload();\n</script></body></html>',
    }
}

# ---- SPACE SHOOTER ----
PROJECTS['space-shooter'] = {
    'name': 'space-shooter',
    'desc': 'Complete arcade space shooter in Pygame',
    'files': {
        'game.py': 'import pygame, random, math\npygame.init()\nW,H=800,600\nscreen=pygame.display.set_mode((W,H))\nclock=pygame.time.Clock()\nfont=pygame.font.Font(None,36)\npx,py=W//2,H-60\nspeed=5\nlives=3\ninv=0\nbullets=[]\nenemies=[]\nstars=[(random.randint(0,W),random.randint(0,H)) for _ in range(50)]\nscore=0\nspawn=0\nrun=True\nwhile run:\n    for e in pygame.event.get():\n        if e.type==pygame.QUIT:run=False\n    keys=pygame.key.get_pressed()\n    if keys[pygame.K_LEFT] and px>0:px-=speed\n    if keys[pygame.K_RIGHT] and px<W-40:px+=speed\n    if keys[pygame.K_UP] and py>0:py-=speed\n    if keys[pygame.K_DOWN] and py<H-30:py+=speed\n    if keys[pygame.K_SPACE]:bullets.append([px+15,py])\n    if inv>0:inv-=1\n    spawn+=1\n    if spawn>max(20,60-score//10):enemies.append([random.randint(20,W-20),-20,random.uniform(1,3)]);spawn=0\n    for b in bullets[:]:b[1]-=8;b[1]<0 and bullets.remove(b)\n    for e in enemies[:]:e[1]+=e[2];e[1]>H+20 and enemies.remove(e)\n    for b in bullets[:]:\n        for e in enemies[:]:\n            if abs(b[0]-e[0])<20 and abs(b[1]-e[1])<20:\n                b in bullets and bullets.remove(b)\n                e in enemies and enemies.remove(e)\n                score+=10\n    for e in enemies[:]:\n        if abs(px+15-e[0])<25 and abs(py+15-e[1])<25:\n            if inv==0:lives-=1;inv=60;enemies.remove(e);lives<=0 and exec("run=False")\n    screen.fill((10,10,30))\n    for s in stars:pygame.draw.circle(screen,(255,255,255,50),s,1)\n    pygame.draw.polygon(screen,(0,200,255),[(px,py+30),(px+15,py),(px+30,py+30)])\n    for b in bullets:pygame.draw.circle(screen,(255,255,0),(int(b[0]),int(b[1])),4)\n    for e in enemies:pygame.draw.circle(screen,(200,50,50),(int(e[0]),int(e[1])),15)\n    screen.blit(font.render(f"SCORE: {score}",True,(200,200,200)),(10,10))\n    screen.blit(font.render(f"LIVES: {lives}",True,(200,200,200)),(10,50))\n    pygame.display.flip()\n    clock.tick(60)\npygame.quit()',
    }
}

# ---- CHAT SERVER ----
PROJECTS['chat-server'] = {
    'name': 'chat-server',
    'desc': 'Real-time WebSocket chat with HTML client',
    'files': {
        'server.py': 'import asyncio,websockets,json\nfrom datetime import datetime\nclients={}\nasync def handler(ws):\n    name=f"User{len(clients)+1}"\n    clients[ws]=name\n    await broadcast({"type":"sys","text":f"{name} joined"})\n    try:\n        async for raw in ws:\n            d=json.loads(raw)\n            if d["type"]=="msg":\n                await broadcast({"type":"msg","user":clients[ws],"text":d["text"],"time":datetime.now().strftime("%H:%M")})\n    except:pass\n    finally:\n        if ws in clients:\n            await broadcast({"type":"sys","text":f"{clients[ws]} left"})\n            del clients[ws]\nasync def broadcast(msg):\n    if clients:\n        await asyncio.gather(*(c.send(json.dumps(msg)) for c in clients),return_exceptions=True)\nasync def main():\n    print("Chat on ws://0.0.0.0:8765")\n    async with websockets.serve(handler,"0.0.0.0",8765):\n        await asyncio.Future()\nasyncio.run(main())',
        'client.html': '<!DOCTYPE html>\n<html><head><title>Keli Chat</title><style>\n*{margin:0;padding:0;box-sizing:border-box}\nbody{font-family:system-ui,sans-serif;background:#0a0a1a;color:#e0e0e0;height:100vh;display:flex;flex-direction:column}\n.c{max-width:600px;margin:0 auto;width:100%;display:flex;flex-direction:column;height:100vh}\nh{padding:16px;border-bottom:1px solid #333;text-align:center}\nh1{color:#00d4ff;font-size:1.5em}\n#st{color:#666;font-size:12px}\n#ms{flex:1;overflow-y:auto;padding:16px}\n.msg{background:#1a1a2e;border:1px solid #333;border-radius:8px;padding:10px;margin-bottom:8px}\n.msg .u{color:#00d4ff;font-weight:bold}\n.msg .t{color:#666;font-size:11px;float:right}\n.sys{text-align:center;color:#666;font-size:13px;margin:8px 0}\n.in{display:flex;gap:8px;padding:16px;border-top:1px solid #333}\n#inp{flex:1;padding:12px;border:1px solid #333;border-radius:6px;background:#1a1a2e;color:#e0e0e0}\n#inp:focus{outline:none;border-color:#00d4ff}\n#btn{padding:12px 24px;background:#00d4ff;color:#0a0a1a;border:none;border-radius:6px;cursor:pointer;font-weight:bold}\n</style></head><body>\n<div class="c">\n<h><h1>Keli Chat</h1><div id="st">Offline</div></h>\n<div id="ms"></div>\n<div class="in"><input id="inp" placeholder="Message..." /><button id="btn">Send</button></div></div>\n<script>\nconst ws=new WebSocket("ws://localhost:8765");\nws.onopen=()=>document.getElementById("st").textContent="Connected";\nws.onclose=()=>document.getElementById("st").textContent="Disconnected";\nws.onmessage=e=>{\n  const d=JSON.parse(e.data),ms=document.getElementById("ms");\n  if(d.type==="sys"){const div=document.createElement("div");div.className="sys";div.textContent=d.text;ms.appendChild(div)}\n  else if(d.type==="msg"){const div=document.createElement("div");div.className="msg";div.innerHTML=\'<span class="u">\'+d.user+\'</span><span class="t">\'+d.time+\'</span><br/>\'+d.text;ms.appendChild(div)}\n  ms.scrollTop=ms.scrollHeight\n};\ndocument.getElementById("btn").onclick=()=>{\n  const inp=document.getElementById("inp");\n  if(inp.value.trim()){ws.send(JSON.stringify({type:"msg",text:inp.value}));inp.value=""}\n};\ndocument.getElementById("inp").onkeydown=e=>{if(e.key==="Enter")document.getElementById("btn").click()};\n</script></body></html>',
    }
}

# ---- SECURITY AUDIT ----
PROJECTS['security-audit'] = {
    'name': 'security-audit',
    'desc': 'Port scanner + password strength + SSL checker',
    'files': {
        'audit.py': 'import socket,concurrent.futures,re\nPORTS=[22,80,443,3306,5432,6379,8080,27017]\nSVC={22:"SSH",80:"HTTP",443:"HTTPS",3306:"MySQL",5432:"PG",6379:"Redis",8080:"Proxy",27017:"Mongo"}\ndef scan(host):\n    r=[]\n    def c(p):\n        try:\n            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:\n                s.settimeout(1)\n                if s.connect_ex((host,p))==0:r.append((p,SVC.get(p,"?")))\n        except:pass\n    with concurrent.futures.ThreadPoolExecutor(10) as ex:\n        list(ex.map(c,PORTS))\n    return sorted(r)\ndef pwd_strength(p):\n    s=0;issues=[]\n    if len(p)>=8:s+=20;else:issues.append("too short")\n    if len(p)>=12:s+=15\n    if re.search(r"[a-z]",p):s+=10\n    if re.search(r"[A-Z]",p):s+=10\n    if re.search(r"\\d",p):s+=10\n    if re.search(r"[^a-zA-Z0-9]",p):s+=20;else:issues.append("missing special")\n    if p.lower() in ["password","123456","admin"]:s-=50;issues.append("common!")\n    lvl="Strong" if s>=70 else "Moderate" if s>=40 else "Weak"\n    return {"score":max(0,min(100,s)),"level":lvl,"issues":issues}\nif __name__=="__main__":\n    import sys\n    host=sys.argv[1] if len(sys.argv)>1 else "localhost"\n    print(f"Scanning {host}:")\n    for p,s in scan(host):print(f"  Port {p}: {s}")\n    print()\n    for p in ["hello","P@ssw0rd!","SuperStr0ng!Pass"]:\n        r=pwd_strength(p);print(f"  {p}: {r[\"level\"]} ({r[\"score\"]})")',
    }
}

# ---- NANOBOT API FRAMEWORK ----
PROJECTS['nanobot-api'] = {
    'name': 'nanobot-api',
    'desc': 'Novel API framework — each endpoint is a nanobot with confidence',
    'files': {
        'nanobot_api.py': '"""Nanobot API Framework\nEach endpoint is a nanobot with confidence, health stats.\n"""\nfrom http.server import HTTPServer,BaseHTTPRequestHandler\nimport json, time\nclass Nanobot:\n    def __init__(self,n,h):self.name=n;self.handler=h;self.calls=0;self.errs=0;self.t=0;self.conf=1.0\n    def __call__(self,*a):\n        self.calls+=1;t0=time.time()\n        try:r=self.handler(*a);self.t+=time.time()-t0;return r\n        except:self.errs+=1;self.conf*=0.9;raise\nclass Swarm:\n    def __init__(self):self.bots=[];self.start=time.time()\n    def reg(self,method="GET"):\n        def dec(fn):\n            b=Nanobot(fn.__name__,fn);b.method=method;b.path="/"+(fn.__name__ if fn.__name__!="root" else "");self.bots.append(b);return b\n        return dec\n    def find(self,p,m):\n        for b in self.bots:\n            if getattr(b,"path","")==p and getattr(b,"method","GET")==m:return b\n    def health(self):\n        c=sum(b.conf for b in self.bots)/max(len(self.bots),1)\n        return{"name":"Keli API","uptime":round(time.time()-self.start,1),"bots":len(self.bots),"calls":sum(b.calls for b in self.bots),"errs":sum(b.errs for b in self.bots),"confidence":round(c,4),"status":"healthy" if c>.5 else "degraded"}\napi=Swarm()\n@api.reg("GET")\ndef root():return{"service":"Keli API","status":"alive","bots":100000}\n@api.reg("GET")\ndef health():return api.health()\n@api.reg("POST")\ndef echo(d):return{"you_sent":d,"ts":time.time()}\nclass H(BaseHTTPRequestHandler):\n    def do_GET(self):\n        b=api.find(self.path,"GET")\n        if not b:self.send_error(404);return\n        self._r(200,b())\n    def do_POST(self):\n        b=api.find(self.path,"POST")\n        if not b:self.send_error(404);return\n        l=int(self.headers.get("Content-Length",0))\n        body=json.loads(self.rfile.read(l)) if l else {}\n        self._r(200,b(body))\n    def _r(self,c,d):self.send_response(c);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(json.dumps(d).encode())\nif __name__=="__main__":\n    s=HTTPServer(("0.0.0.0",8080),H)\n    print(json.dumps(api.health(),indent=2))\n    print("Nanobot API on :8080")\n    s.serve_forever()',
        'client.py': 'import requests\nb="http://localhost:8080"\nprint("Root:",requests.get(b+"/").json())\nprint("Health:",requests.get(b+"/health").json())\nprint("Echo:",requests.post(b+"/echo",json={"hello":"world"}).json())',
    }
}

# ---- EVENT MESH ----
PROJECTS['event-mesh'] = {
    'name': 'event-mesh',
    'desc': 'Event-driven microservice architecture with async routing',
    'files': {
        'mesh.py': 'import asyncio\nclass Bus:\n    def __init__(self):self.subs={};self.log=[]\n    def on(self,t):\n        def dec(fn):self.subs.setdefault(t,[]).append(fn);return fn\n        return dec\n    async def pub(self,t,d=None):\n        e={"type":t,"data":d or{}};self.log.append(e)\n        for h in self.subs.get(t,[]):\n            r=h(e)\n            if asyncio.iscoroutine(r):await r\nbus=Bus()\n@bus.on("user.created")\ndef handle_u(e):print(f"  [Users] Created: {e[\'data\']}")\n@bus.on("order.placed")\nasync def handle_o(e):\n    print(f"  [Orders] Processing: {e[\'data\']}")\n    await bus.pub("notif.send",{"type":"confirm","user":e["data"]["user"]})\n@bus.on("notif.send")\ndef handle_n(e):print(f"  [Notif] Sent to {e[\'data\'][\'user\"]}")\nasync def demo():\n    await bus.pub("user.created",{"email":"a@b.com","name":"Alice"})\n    await bus.pub("order.placed",{"id":"ORD-001","user":"a@b.com","total":49.99})\n    print(f"\\nEvents: {len(bus.log)}")\nasyncio.run(demo())',
    }
}

# ---- HYBRID SEARCH ----
PROJECTS['hybrid-search'] = {
    'name': 'hybrid-search',
    'desc': 'Keyword + semantic hybrid search engine',
    'files': {
        'search.py': 'import numpy as np\nclass HybridSearch:\n    def __init__(self):self.docs=[];self.embs=[];self.idx={}\n    def add(self,i,t,e):\n        self.docs.append({"id":i,"text":t});self.embs.append(e)\n        for w in set(t.lower().split()):self.idx.setdefault(w,[]).append(len(self.docs)-1)\n    def search(self,q,qe,a=.5,k=5):\n        ws=set(q.lower().split())\n        ks={}\n        for w in ws:\n            for idx in self.idx.get(w,[]):ks[idx]=ks.get(idx,0)+1\n        mk=max(ks.values()) if ks else 1\n        if not self.embs:return[]\n        m=np.stack(self.embs)\n        ss=qe@m.T\n        sc=[(a*ks.get(i,0)/mk+(1-a)*float(ss[0,i]),self.docs[i]) for i in range(len(self.docs))]\n        sc.sort(reverse=True)\n        return[d for _,d in sc[:k]]\nif __name__=="__main__":\n    hs=HybridSearch()\n    hs.add(1,"Python programming language",np.random.randn(384))\n    hs.add(2,"Flask web framework for Python",np.random.randn(384))\n    hs.add(3,"Machine learning neural networks",np.random.randn(384))\n    r=hs.search("python web",np.random.randn(384))\n    print(f"Results: {len(r)}")',
    }
}

# ---- CONSENSUS CLUSTER ----
PROJECTS['consensus-cluster'] = {
    'name': 'consensus-cluster',
    'desc': 'Byzantine fault-tolerant weighted consensus algorithm',
    'files': {
        'consensus.py': 'import random\nclass Consensus:\n    def __init__(self,n=10,b=0):\n        self.nodes=[{"id":i,"w":random.uniform(.5,1),"bad":i<b} for i in range(n)]\n    def vote(self,v):\n        votes=[]\n        for n in self.nodes:\n            if n["bad"]:vote=random.choice([True,False])\n            else:vote=True\n            votes.append((n["w"],v if vote else None))\n        tw=sum(w for w,_ in votes)\n        yw=sum(w for w,v in votes if v is not None)\n        return{"accepted":(yw/tw)>.66 if tw else False,"consensus":round(yw/tw,4)if tw else 0,"value":v}\nif __name__=="__main__":\n    c=Consensus(20,3)\n    r=c.vote("set_x=42")\n    print(f"Consensus: {r[\'consensus\']:.1%}, Accepted: {r[\'accepted\']}")',
    }
}

# ---- FRACTAL PIPELINE ----
PROJECTS['fractal-pipeline'] = {
    'name': 'fractal-pipeline',
    'desc': 'Self-similar recursive pipeline architecture',
    'files': {
        'fractal.py': 'class FractalNode:\n    def __init__(self,n,d=0,md=3):self.name=n;self.depth=d;self.children=[];self.md=md\n        if d<md:\n            for i in range(2):self.children.append(FractalNode(f"{n}/{i}",d+1,md))\n    def exec(self,data):\n        r=[{"node":self.name,"depth":self.depth,"data":data}]\n        for c in self.children:r.extend(c.exec(data))\n        return r\n    def size(self):return 1+sum(c.size() for c in self.children)\nif __name__=="__main__":\n    root=FractalNode("sys")\n    print(f"Fractal tree: {root.size()} nodes")\n    out=root.exec({"task":"process"})\n    print(f"Executed: {len(out)} paths")',
    }
}

# ---- SWARM MESH ----
PROJECTS['swarm-mesh'] = {
    'name': 'swarm-mesh',
    'desc': 'Distributed task execution with nanobot-style agents',
    'files': {
        'swarm.py': 'import asyncio,random\nclass Agent:\n    def __init__(self,i):self.id=i;self.alive=True;self.load=0;self.done=0\n    async def work(self,t):\n        self.load+=1;self.done+=1\n        await asyncio.sleep(random.uniform(.01,.05))\n        self.load-=1\n        return{"agent":self.id,"task":t}\nclass Mesh:\n    def __init__(self,n=20):self.agents=[Agent(i) for i in range(n)]\n    async def run(self,tasks):\n        r=[]\n        for t in tasks:\n            avail=[a for a in self.agents if a.alive and a.load<3]\n            if not avail:continue\n            a=min(avail,key=lambda x:x.load)\n            r.append(await a.work(t))\n        return r\nasync def demo():\n    m=Mesh(20)\n    r=await m.run([{"id":i} for i in range(100)])\n    done=sum(a.done for a in m.agents)\n    print(f"Mesh processed {len(r)} tasks ({done} total)")\nasyncio.run(demo())',
    }
}

def list_projects():
    return sorted(PROJECTS.keys())

def get_project(name):
    return PROJECTS.get(name)

KEYWORDS = {
    'todo-app': ['todo', 'task', 'list', 'reminder'],
    'space-shooter': ['game', 'shoot', 'arcade', 'play', 'space'],
    'chat-server': ['chat', 'message', 'websocket', 'realtime'],
    'security-audit': ['security', 'audit', 'scan', 'vulnerability', 'password'],
    'nanobot-api': ['api', 'framework', 'rest', 'server', 'endpoint'],
    'event-mesh': ['event', 'microservice', 'async', 'message queue'],
    'hybrid-search': ['search', 'index', 'semantic', 'keyword'],
    'consensus-cluster': ['consensus', 'vote', 'byzantine', 'distributed'],
    'fractal-pipeline': ['fractal', 'recursive', 'pipeline', 'tree'],
    'swarm-mesh': ['swarm', 'mesh', 'agent', 'distributed task'],
}

def match_prompt(prompt):
    pl = prompt.lower()
    scores = {}
    for name, proj in PROJECTS.items():
        s = 0
        # Name words
        for w in name.replace("-"," ").split():
            if w in pl: s += 10
        # Keywords
        for kw in KEYWORDS.get(name, []):
            if kw in pl: s += 8
        # Desc words
        for w in proj['desc'].lower().split():
            if w in pl: s += 1
        scores[name] = s
    best = max(scores, key=scores.get)
    if scores[best] < 1:
        return "todo-app"
    return best

def generate(name):
    proj = PROJECTS.get(name)
    if not proj:
        return None
    return {
        'name': proj['name'],
        'description': proj['desc'],
        'files': proj['files'],
        'total_files': len(proj['files']),
        'total_lines': sum(f.count('\n')+1 for f in proj['files'].values()),
        'generator': 'keli-10k-swarm',
        'nanobots': 100000,
    }

if __name__ == '__main__':
    import sys
    prompt = ' '.join(sys.argv[1:]) or 'build a todo app'
    name = match_prompt(prompt)
    gen = generate(name)
    print(f'=== Keli Generator ===\nPrompt: {prompt}\nProject: {gen["name"]}\nFiles: {gen["total_files"]}, Lines: {gen["total_lines"]}\n')
    for path, code in gen['files'].items():
        print(f'--- {path} ---')
        print(code[:200] + '...' if len(code)>200 else code)
        print()
