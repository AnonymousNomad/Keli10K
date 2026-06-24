(function() {
  'use strict';

  let canvas, ctx;
  let nodes = [];
  let connections = [];
  let animFrame = null;
  let visible = false;
  let hoveredNode = null;
  let draggingNode = null;
  let dragOffset = { x: 0, y: 0 };
  let scale = 1;
  let offsetX = 0, offsetY = 0;
  let tooltipEl = null;

  const NODE_COLORS = {
    html: '#00e5ff',
    css: '#00ffc8',
    js: '#b967ff',
    python: '#7c3aed',
    state: '#00ffc8',
    error: '#ff6b00',
  };

  const NODE_LABELS = {
    html: 'HTML',
    css: 'CSS',
    js: 'JS',
    python: 'PY',
    state: 'STATE',
    error: 'ERR',
  };

  function init(containerId) {
    const container = document.getElementById(containerId) || document.createElement('div');
    canvas = document.createElement('canvas');
    canvas.className = 'blueprint-canvas';
    canvas.style.cssText = 'position:absolute;inset:0;z-index:5;pointer-events:auto;';
    container.appendChild(canvas);
    ctx = canvas.getContext('2d');

    resize();
    window.addEventListener('resize', debounce(resize, 200));

    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseUp);
    canvas.addEventListener('dblclick', onDoubleClick);
    canvas.addEventListener('wheel', onWheel, { passive: false });

    tooltipEl = document.createElement('div');
    tooltipEl.className = 'node-tooltip';
    document.body.appendChild(tooltipEl);

    container.classList.add('blueprint-container');
    container.style.display = visible ? 'block' : 'none';
  }

  function resize() {
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;
    canvas.width = parent.clientWidth || window.innerWidth;
    canvas.height = parent.clientHeight || window.innerHeight;
    render();
  }

  function debounce(fn, ms) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
  }

  function addNode(id, type, x, y, label) {
    nodes.push({
      id, type, label: label || NODE_LABELS[type] || type,
      x, y, radius: 30, color: NODE_COLORS[type] || '#00e5ff',
      opacity: 1, glow: 0, pulse: 0,
    });
    render();
  }

  function addConnection(fromId, toId, type) {
    connections.push({ from: fromId, to: toId, type: type || 'solid', progress: 0 });
    render();
  }

  function clearNodes() {
    nodes = [];
    connections = [];
    render();
  }

  function removeNode(id) {
    nodes = nodes.filter(n => n.id !== id);
    connections = connections.filter(c => c.from !== id && c.to !== id);
    render();
  }

  function glowNode(id) {
    const node = nodes.find(n => n.id === id);
    if (node) {
      node.glow = 1;
      animateGlow(node);
    }
  }

  function animateGlow(node) {
    if (!node) return;
    const start = performance.now();
    function step(now) {
      const t = (now - start) / 500;
      if (t >= 1) { node.glow = 0; render(); return; }
      node.glow = 1 - t;
      render();
      requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function pulseAll() {
    nodes.forEach((n, i) => {
      setTimeout(() => {
        n.pulse = 1;
        const start = performance.now();
        function step(now) {
          const t = (now - start) / 400;
          if (t >= 1) { n.pulse = 0; return; }
          n.pulse = 1 - t;
          render();
          requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      }, i * 200);
    });
  }

  function show() { visible = true; if (canvas) canvas.parentElement.style.display = 'block'; render(); }
  function hide() { visible = false; if (canvas) canvas.parentElement.style.display = 'none'; }
  function toggle() { visible ? hide() : show(); }

  function render() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.translate(offsetX, offsetY);
    ctx.scale(scale, scale);

    const sectorLabels = {};
    const activeSectors = {};

    nodes.forEach(node => {
      if (!sectorLabels[node.type]) {
        sectorLabels[node.type] = { x: node.x, y: node.y, count: 0 };
      }
      sectorLabels[node.type].x += node.x;
      sectorLabels[node.type].y += node.y;
      sectorLabels[node.type].count++;
    });

    connections.forEach(conn => {
      const from = nodes.find(n => n.id === conn.from);
      const to = nodes.find(n => n.id === conn.to);
      if (!from || !to) return;

      ctx.beginPath();
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x, to.y);

      if (conn.type === 'dashed') {
        ctx.setLineDash([6, 4]);
      } else if (conn.type === 'glow') {
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#00ffc8';
      } else if (conn.type === 'error') {
        ctx.strokeStyle = '#ff6b00';
        ctx.setLineDash([3, 3]);
      } else {
        ctx.strokeStyle = 'rgba(0, 229, 255, 0.3)';
      }

      ctx.stroke();
      ctx.setLineDash([]);
      ctx.shadowBlur = 0;

      // Data packet animation
      conn.progress = (conn.progress + 0.005) % 1;
      const packetX = from.x + (to.x - from.x) * conn.progress;
      const packetY = from.y + (to.y - from.y) * conn.progress;
      ctx.beginPath();
      ctx.arc(packetX, packetY, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#00ffc8';
      ctx.fill();
      ctx.shadowBlur = 6;
      ctx.shadowColor = '#00ffc8';
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    nodes.forEach(node => {
      ctx.save();
      ctx.globalAlpha = node.opacity * (visible ? 1 : 0);

      // Glow
      if (node.glow > 0) {
        ctx.shadowBlur = 30 * node.glow;
        ctx.shadowColor = node.color;
      }

      // Pulse
      const r = node.radius + (node.pulse * 10);

      // Node shape
      ctx.beginPath();
      if (node.type === 'state') {
        ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
      } else {
        roundRect(ctx, node.x - r, node.y - r * 0.7, r * 2, r * 1.4, 8);
      }

      ctx.fillStyle = node.color + '22';
      ctx.fill();
      ctx.strokeStyle = node.color;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Label
      ctx.fillStyle = node.color;
      ctx.font = 'bold 11px monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.label, node.x, node.y);

      ctx.restore();
    });

    // Sector labels
    Object.entries(sectorLabels).forEach(([type, pos]) => {
      if (pos.count === 0) return;
      const cx = pos.x / pos.count;
      const cy = pos.y / pos.count - 80;
      ctx.fillStyle = 'rgba(0, 229, 255, 0.15)';
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(type.toUpperCase() + ' SECTOR', cx, cy);
    });

    ctx.restore();

    // Animation loop
    if (visible) {
      animFrame = requestAnimationFrame(render);
    }
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
  }

  function getNodeAt(mx, my) {
    const cx = (mx - offsetX) / scale;
    const cy = (my - offsetY) / scale;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      const dx = cx - n.x, dy = cy - n.y;
      if (Math.sqrt(dx*dx + dy*dy) < n.radius + 10) return n;
    }
    return null;
  }

  function onMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    if (draggingNode) {
      draggingNode.x = (mx - offsetX) / scale - dragOffset.x;
      draggingNode.y = (my - offsetY) / scale - dragOffset.y;
      return;
    }

    const node = getNodeAt(mx, my);
    canvas.style.cursor = node ? 'pointer' : 'default';

    if (node !== hoveredNode) {
      hoveredNode = node;
      if (node && tooltipEl) {
        tooltipEl.style.display = 'block';
        tooltipEl.style.left = (e.clientX + 12) + 'px';
        tooltipEl.style.top = (e.clientY + 12) + 'px';
        tooltipEl.textContent = `${node.label} (${node.id})`;
      } else if (tooltipEl) {
        tooltipEl.style.display = 'none';
      }
    } else if (node && tooltipEl) {
      tooltipEl.style.left = (e.clientX + 12) + 'px';
      tooltipEl.style.top = (e.clientY + 12) + 'px';
    }
  }

  function onMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const node = getNodeAt(mx, my);
    if (node) {
      draggingNode = node;
      dragOffset.x = (mx - offsetX) / scale - node.x;
      dragOffset.y = (my - offsetY) / scale - node.y;
    }
  }

  function onMouseUp() {
    draggingNode = null;
  }

  function onDoubleClick(e) {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const node = getNodeAt(mx, my);
    if (node && window.KeliFileTree && window.KeliFileTree.openFile) {
      window.KeliFileTree.openFile(node.id);
    }
  }

  function onWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    scale = Math.max(0.3, Math.min(3, scale * delta));
    render();
  }

  window.KeliBlueprint = { init, addNode, addConnection, clearNodes, removeNode, glowNode, pulseAll, show, hide, toggle, render };
})();
