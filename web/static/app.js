/**
 * Mini-Python IDE — Frontend Application Logic
 * ==============================================
 * Handles: code execution, tab switching, line numbers, snippets, keyboard shortcuts.
 */

// ── DOM Elements ────────────────────────────────────────────────
const editor       = document.getElementById('code-editor');
const lineNumbers  = document.getElementById('line-numbers');
const btnRun       = document.getElementById('btn-run');
const btnClear     = document.getElementById('btn-clear');
const outputArea   = document.getElementById('output-area');
const variablesArea = document.getElementById('variables-area');
const astArea      = document.getElementById('ast-area');
const statusDot    = document.querySelector('.status-dot');
const statusText   = document.querySelector('.status-text');
const outputPanel  = document.getElementById('output-section');

// ── Example Snippets ────────────────────────────────────────────
const SNIPPETS = {
    arithmetic: `x = 10
y = 3
print(x + y)
print(x - y)
print(x * y)
print(x / y)`,

    variables: `celsius = 100
fahrenheit = celsius * 9 / 5 + 32
print(fahrenheit)

a = 5
b = a * 2 + 1
print(b)`,

    conditionals: `score = 85
if score == 100:
    print(True)

x = 42
if x == 42:
    print(x)`,

    types: `age = 25
price = 9.99
grade = 'A'
passed = True

print(age)
print(price)
print(grade)
print(passed)
print(not passed)`
};

// ── Line Numbers ────────────────────────────────────────────────
function updateLineNumbers() {
    const lines = editor.value.split('\n');
    const count = Math.max(lines.length, 1);
    let html = '';
    for (let i = 1; i <= count; i++) {
        html += i + '\n';
    }
    lineNumbers.textContent = html;
}

editor.addEventListener('input', updateLineNumbers);
editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
});

// Initialize line numbers
updateLineNumbers();

// ── Tab key support ─────────────────────────────────────────────
editor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.value = editor.value.substring(0, start) + '    ' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + 4;
        updateLineNumbers();
    }
});

// ── Tab Switching ───────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Deactivate all tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Activate clicked tab
        tab.classList.add('active');
        const targetId = 'tab-' + tab.dataset.tab;
        document.getElementById(targetId).classList.add('active');
    });
});

// ── Snippet Buttons ─────────────────────────────────────────────
document.querySelectorAll('.snippet-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const key = btn.dataset.snippet;
        if (SNIPPETS[key]) {
            editor.value = SNIPPETS[key];
            updateLineNumbers();
            editor.focus();
        }
    });
});

// ── Status Helpers ──────────────────────────────────────────────
function setStatus(state, text) {
    statusDot.className = 'status-dot' + (state !== 'ready' ? ' ' + state : '');
    statusText.textContent = text;
}

// ── Output Helpers ──────────────────────────────────────────────
function clearOutput() {
    outputArea.innerHTML = '';
    variablesArea.innerHTML = '';
    astArea.innerHTML = '';
}

function addOutputLine(text, className) {
    const div = document.createElement('div');
    div.className = 'output-line ' + className;
    div.textContent = text;
    outputArea.appendChild(div);
}

function addOutputHTML(html, className) {
    const div = document.createElement('div');
    div.className = 'output-line ' + className;
    div.innerHTML = html;
    outputArea.appendChild(div);
}

// ── Render Variables Table ──────────────────────────────────────
function renderVariables(variables) {
    const entries = Object.entries(variables);
    if (entries.length === 0) {
        variablesArea.innerHTML = `
            <div class="output-placeholder">
                <div class="placeholder-icon">📦</div>
                <p>No variables defined</p>
            </div>`;
        return;
    }

    let html = `<table class="var-table">
        <thead>
            <tr><th>Name</th><th>Value</th><th>Type</th></tr>
        </thead>
        <tbody>`;

    for (const [name, info] of entries) {
        html += `<tr>
            <td><span class="var-name">${escapeHtml(name)}</span></td>
            <td><span class="var-value">${escapeHtml(info.value)}</span></td>
            <td><span class="var-type type-${info.type}">${info.type}</span></td>
        </tr>`;
    }

    html += '</tbody></table>';
    variablesArea.innerHTML = html;
}

// ── Render AST ──────────────────────────────────────────────────
function renderAST(astText) {
    if (!astText) {
        astArea.innerHTML = `
            <div class="output-placeholder">
                <div class="placeholder-icon">🌳</div>
                <p>AST not available</p>
            </div>`;
        return;
    }
    astArea.textContent = astText;
}

// ── HTML escape ─────────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ── Run Code ────────────────────────────────────────────────────
async function runCode() {
    const code = editor.value;

    if (!code.trim()) {
        clearOutput();
        addOutputLine('No code to execute.', 'error-message');
        return;
    }

    // UI feedback
    setStatus('running', 'Executing...');
    btnRun.classList.add('running');
    clearOutput();

    const startTime = performance.now();

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        });

        const data = await response.json();
        const elapsed = (performance.now() - startTime).toFixed(0);

        if (data.success) {
            // ✅ Success
            setStatus('ready', 'Success');
            addOutputHTML('✓ Execution successful', 'success-banner');

            // Print output lines
            if (data.output && data.output.trim()) {
                const lines = data.output.split('\n');
                for (const line of lines) {
                    if (line !== '') {
                        addOutputLine(line, 'stdout');
                    }
                }
            } else {
                addOutputLine('(no output)', 'stdout');
            }

            addOutputLine(`Completed in ${elapsed}ms`, 'timing');

            // Flash success
            outputPanel.classList.add('flash-success');
            setTimeout(() => outputPanel.classList.remove('flash-success'), 600);

        } else {
            // ❌ Error
            setStatus('error', data.error.type);

            addOutputHTML(`✗ ${escapeHtml(data.error.type)}`, 'error-banner');

            if (data.error.stage) {
                addOutputLine(`Stage: ${data.error.stage}`, 'error-stage');
            }

            addOutputLine(data.error.message, 'error-message');
            addOutputLine(`Failed after ${elapsed}ms`, 'timing');

            // Flash error
            outputPanel.classList.add('flash-error');
            setTimeout(() => outputPanel.classList.remove('flash-error'), 600);

            // Reset status after delay
            setTimeout(() => setStatus('ready', 'Ready'), 3000);
        }

        // Update variables and AST tabs
        renderVariables(data.variables || {});
        renderAST(data.ast_preview);

        // Switch to output tab
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelector('[data-tab="output"]').classList.add('active');
        document.getElementById('tab-output').classList.add('active');

    } catch (err) {
        setStatus('error', 'Connection Error');
        addOutputLine('Failed to connect to the interpreter server.', 'error-message');
        addOutputLine('Make sure the server is running: python web_app.py', 'error-stage');
        setTimeout(() => setStatus('ready', 'Ready'), 3000);
    } finally {
        btnRun.classList.remove('running');
    }
}

// ── Event Bindings ──────────────────────────────────────────────
btnRun.addEventListener('click', runCode);

btnClear.addEventListener('click', () => {
    editor.value = '';
    updateLineNumbers();
    clearOutput();
    outputArea.innerHTML = `
        <div class="output-placeholder">
            <div class="placeholder-icon">⚡</div>
            <p>Run your code to see output here</p>
            <p class="placeholder-hint">Press <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to execute</p>
        </div>`;
    variablesArea.innerHTML = `
        <div class="output-placeholder">
            <div class="placeholder-icon">📦</div>
            <p>Variable states will appear here after execution</p>
        </div>`;
    astArea.innerHTML = `
        <div class="output-placeholder">
            <div class="placeholder-icon">🌳</div>
            <p>Abstract Syntax Tree visualization</p>
        </div>`;
    editor.focus();
});

// ── Keyboard Shortcut: Ctrl+Enter to run ────────────────────────
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
    }
});
