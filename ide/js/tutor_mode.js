(function() {
  'use strict';

  let active = false;
  let currentStep = 0;
  let steps = [];
  let lessonTask = '';
  let panelEl = null;

  const LESSON_TEMPLATES = {
    'todo app': {
      task: 'Build a todo app',
      steps: [
        { title: 'HTML Structure', explanation: 'Every app starts with a skeleton. This div holds everything.', code: '<div id="app"></div>\n<input id="todo-input" placeholder="Add a task...">\n<ul id="todo-list"></ul>', user_action: 'watch', checkpoint: false },
        { title: 'CSS Styling', explanation: 'Make it look good. Flexbox for layout, colors for clarity.', code: '#app { max-width: 400px; margin: 0 auto; font-family: sans-serif; }\n#todo-input { width: 100%; padding: 8px; }\n#todo-list { list-style: none; padding: 0; }', user_action: 'watch', checkpoint: false },
        { title: 'State Management', explanation: 'Now the brains. useState stores our todos array.', code: 'const [todos, setTodos] = useState([]);\nconst [input, setInput] = useState("");', user_action: 'write', checkpoint: true, hint: 'You need setTodos and the initial value.' },
        { title: 'Add Todo', explanation: 'Handle adding a new todo from the input field.', code: 'const addTodo = () => {\n  if (input.trim()) {\n    setTodos([...todos, { id: Date.now(), text: input.trim(), done: false }]);\n    setInput("");\n  }\n};', user_action: 'write', checkpoint: true, hint: 'Spread the existing todos array and add a new todo object.' },
        { title: 'Toggle & Delete', explanation: 'Mark todos complete or remove them.', code: 'const toggleTodo = (id) => setTodos(todos.map(t => t.id === id ? {...t, done: !t.done} : t));\nconst deleteTodo = (id) => setTodos(todos.filter(t => t.id !== id));', user_action: 'write', checkpoint: true, hint: 'Use map for toggle, filter for delete.' },
        { title: 'Render List', explanation: 'Display all todos on screen.', code: 'return (\n  <div>\n    <input value={input} onChange={e => setInput(e.target.value)} />\n    <button onClick={addTodo}>Add</button>\n    <ul>\n      {todos.map(t => (\n        <li key={t.id} onClick={() => toggleTodo(t.id)}>\n          {t.text} <button onClick={() => deleteTodo(t.id)}>X</button>\n        </li>\n      ))}\n    </ul>\n  </div>\n);', user_action: 'watch', checkpoint: false },
        { title: 'You Built It!', explanation: 'You just built a complete React todo app. State, events, rendering. Not bad.', code: 'Congratulations! 🎉', user_action: 'celebrate', checkpoint: false },
      ]
    },
    'calculator': {
      task: 'Build a calculator',
      steps: [
        { title: 'HTML Buttons', explanation: 'A calculator needs buttons. Grid them up.', code: '<div className="calculator">\n  <div className="display">0</div>\n  <div className="buttons">\n    {["7","8","9","/","4","5","6","*","1","2","3","-","0",".","=","+"].map(b => (\n      <button key={b} onClick={() => handleClick(b)}>{b}</button>\n    ))}\n  </div>\n</div>', user_action: 'watch', checkpoint: false },
        { title: 'Calculator Logic', explanation: 'Evaluate expressions. Handle the edge cases.', code: 'const [display, setDisplay] = useState("0");\nconst [formula, setFormula] = useState("");\n\nconst handleClick = (val) => {\n  if (val === "=") {\n    try { setDisplay(eval(formula).toString()); } catch { setDisplay("Error"); }\n  } else {\n    setFormula(f => f + val);\n    setDisplay(formula + val);\n  }\n};', user_action: 'write', checkpoint: true, hint: 'Use eval carefully. The formula accumulates button presses.' },
        { title: 'Clear & Style', explanation: 'Add a clear button and make it look like a real calculator.', code: 'const clear = () => { setDisplay("0"); setFormula(""); };\n// Style:\n.buttons { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; }\n.display { background: #222; color: white; padding: 20px; text-align: right; font-size: 24px; }', user_action: 'write', checkpoint: false },
      ]
    },
  };

  function init() {
    panelEl = document.createElement('div');
    panelEl.className = 'tutor-panel';
    panelEl.innerHTML = `
      <div class="tutor-header">
        <div class="tutor-step-number">Step 0 of 0</div>
        <div class="tutor-step-title">Tutor Mode</div>
      </div>
      <div class="tutor-content">
        <div class="tutor-explanation">Ask Keli to teach you something. Try "Teach me to build a todo app" or "Build a calculator".</div>
      </div>
      <div class="tutor-footer">
        <button class="tutor-btn" id="tutor-prev" disabled>Back</button>
        <button class="tutor-btn primary" id="tutor-next">Next Step</button>
      </div>
    `;
    document.body.appendChild(panelEl);

    document.getElementById('tutor-next').addEventListener('click', nextStep);
    document.getElementById('tutor-prev').addEventListener('click', prevStep);
  }

  function loadLesson(task) {
    const template = LESSON_TEMPLATES[task.toLowerCase()] || findClosestLesson(task.toLowerCase());
    if (!template) {
      showMessage('No lesson found for "' + task + '". Try "Build a todo app" or "Build a calculator".');
      return false;
    }

    lessonTask = template.task;
    steps = template.steps;
    currentStep = 0;
    showStep(0);
    activate();
    return true;
  }

  function findClosestLesson(query) {
    for (const [key, lesson] of Object.entries(LESSON_TEMPLATES)) {
      if (query.includes(key) || key.includes(query)) return lesson;
    }
    return null;
  }

  function showStep(index) {
    if (!panelEl || index < 0 || index >= steps.length) return;
    const step = steps[index];

    panelEl.querySelector('.tutor-step-number').textContent = `Step ${index + 1} of ${steps.length}`;
    panelEl.querySelector('.tutor-step-title').textContent = step.title;
    panelEl.querySelector('.tutor-explanation').innerHTML = step.explanation + 
      (step.code ? `<pre class="tutor-code">${step.code}</pre>` : '');

    document.getElementById('tutor-prev').disabled = index === 0;
    const nextBtn = document.getElementById('tutor-next');
    nextBtn.textContent = index === steps.length - 1 ? 'Complete' : 'Next Step';
    nextBtn.disabled = step.checkpoint && step.user_action === 'write';

    if (step.checkpoint && step.user_action === 'write') {
      // Show code input for user to write
      const content = panelEl.querySelector('.tutor-content');
      const inputArea = document.createElement('textarea');
      inputArea.className = 'tutor-code-input';
      inputArea.placeholder = 'Write your code here...';
      inputArea.style.cssText = 'width:100%;height:80px;margin-top:8px;background:rgba(0,0,0,0.3);border:1px solid rgba(192,214,228,0.2);border-radius:4px;padding:8px;color:#e0f7fa;font-family:monospace;font-size:12px;';
      inputArea.id = 'tutor-code-input';
      content.appendChild(inputArea);

      inputArea.addEventListener('input', () => {
        nextBtn.disabled = inputArea.value.trim().length < 5;
      });
    }

    // Update blueprint
    if (window.KeliBlueprint) {
      window.KeliBlueprint.clearNodes();
      const types = ['html', 'css', 'js', 'js', 'js', 'js', 'state'];
      const xOffset = (index - steps.length / 2) * 100;
      for (let i = 0; i <= index; i++) {
        const n = steps[i];
        const type = types[i] || 'js';
        const opacity = i === index ? 1.0 : (i < index ? 0.6 : 0.2);
        window.KeliBlueprint.addNode(
          `step-${i}`, type,
          400 + i * 80 - steps.length * 40, 300,
          `${i+1}. ${n.title.substring(0, 8)}`
        );
      }
      if (index > 0) {
        window.KeliBlueprint.addConnection(`step-${index-1}`, `step-${index}`, 'solid');
      }
      window.KeliBlueprint.show();
    }
  }

  function nextStep() {
    if (currentStep >= steps.length - 1) {
      completeLesson();
      return;
    }

    currentStep++;
    // Remove old code input
    const oldInput = document.getElementById('tutor-code-input');
    if (oldInput) oldInput.remove();

    showStep(currentStep);
  }

  function prevStep() {
    if (currentStep <= 0) return;
    currentStep--;
    const oldInput = document.getElementById('tutor-code-input');
    if (oldInput) oldInput.remove();
    showStep(currentStep);
  }

  function completeLesson() {
    showMessage(`You completed "${lessonTask}"! Certificate generated.`);
    if (window.KeliCertificate) {
      window.KeliCertificate.generate(lessonTask);
    }
    deactivate();
  }

  function activate() {
    active = true;
    panelEl.classList.add('active');
    if (window.KeliAudio) window.KeliAudio.setState('tutor');
  }

  function deactivate() {
    active = false;
    panelEl.classList.remove('active');
    if (window.KeliAudio) window.KeliAudio.setState('idle');
    if (window.KeliBlueprint) window.KeliBlueprint.hide();
  }

  function toggle() {
    active ? deactivate() : init();
  }

  function showMessage(msg) {
    const content = panelEl.querySelector('.tutor-content');
    content.innerHTML = `<div class="tutor-explanation">${msg}</div>`;
  }

  function isActive() { return active; }

  window.KeliTutor = { init, loadLesson, nextStep, prevStep, toggle, isActive, activate, deactivate };
})();
