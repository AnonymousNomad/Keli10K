const API_BASE = (function() {
  const host = window.location.hostname;
  const port = window.location.port || (host === 'localhost' || host === '127.0.0.1' ? '8085' : '');
  return port ? `http://${host}:${port}` : '';
})();

const API_ERRORS = {
  'fetch': 'Keli is sleeping. Start the API server.',
  '500': 'Even Keli can\'t fix the server, dumbass.',
  'timeout': 'Keli\'s taking her time. Probably arguing with the nanobots.',
};

async function _api(path, body, timeoutMs=15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const resp = await fetch(API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!resp.ok) {
      throw new Error(resp.status === 500 ? '500' : `HTTP ${resp.status}`);
    }
    return await resp.json();
  } catch (e) {
    clearTimeout(timer);
    if (e.name === 'AbortError') throw new Error('timeout');
    if (e.message === '500') throw new Error('500');
    throw new Error('fetch');
  }
}

const api = {
  async chat(message, sessionId) {
    return _api('/chat', { query: message, session_id: sessionId || null });
  },

  async build(task, existingFiles, sessionId) {
    return _api('/build', {
      task: task,
      existing_files: existingFiles || {},
      session_id: sessionId || null,
    });
  },

  async preview(files) {
    return _api('/preview', { files: files || {} });
  },

  async export(files, format) {
    return _api('/export', { files: files || {}, format: format || 'static' });
  },

  async run(code, type) {
    return _api('/run', { code: code, type: type || 'js' });
  },

  async download(zipPath) {
    const resp = await fetch(API_BASE + '/download/' + zipPath);
    if (!resp.ok) throw new Error('Download failed');
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = zipPath.split('/').pop() || 'project.zip';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    return true;
  },

  async health() {
    try {
      const resp = await fetch(API_BASE + '/health');
      if (!resp.ok) return { status: 'error' };
      return await resp.json();
    } catch {
      return { status: 'error' };
    }
  },

  getUserError(err) {
    const msg = err && err.message ? err.message : 'fetch';
    return API_ERRORS[msg] || 'Something went wrong. Try again.';
  },
};
