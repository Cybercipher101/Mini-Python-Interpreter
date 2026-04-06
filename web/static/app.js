/**
 * Mini-Python Compiler Visualizer IDE — Frontend v2.0
 * =====================================================
 * Orchestrates: Lexer panel, Syntax panel, Semantic panel,
 *               Validator panel, Executor panel, AST tree.
 */

'use strict';

// ── DOM References ────────────────────────────────────────────────
const editor       = document.getElementById('code-editor');
const lineNumbers  = document.getElementById('line-numbers');
const btnRun       = document.getElementById('btn-run');
const btnClear     = document.getElementById('btn-clear');
const btnExpandAll = document.getElementById('btn-expand-all');
const btnCollapseAll = document.getElementById('btn-collapse-all');
const statusDot    = document.getElementById('status-dot');
const statusText   = document.getElementById('status-text');

// Stage bodies
const bodyLexer    = document.getElementById('body-lexer');
const bodySyntax   = document.getElementById('body-syntax');
const bodySemantic = document.getElementById('body-semantic');
const bodyValidator= document.getElementById('body-validator');
const bodyExecutor = document.getElementById('body-executor');
const astBody      = document.getElementById('ast-body');

// Stage badges
const badgeLexer    = document.getElementById('badge-lexer');
const badgeSyntax   = document.getElementById('badge-syntax');
const badgeSemantic = document.getElementById('badge-semantic');
const badgeValidator= document.getElementById('badge-validator');
const badgeExecutor = document.getElementById('badge-executor');

// Stage panels (for flash animation)
const panelLexer    = document.getElementById('panel-lexer');
const panelSyntax   = document.getElementById('panel-syntax');
const panelSemantic = document.getElementById('panel-semantic');
const panelValidator= document.getElementById('panel-validator');
const panelExecutor = document.getElementById('panel-executor');

// ── Example Snippets ──────────────────────────────────────────────
const SNIPPETS = {
    arithmetic: `x = 10
y = 3
print(x + y)
print(x - y)
print(x * y)
print(x / y)
print(x // y)
print(x % y)
print(x ** y)`,

    conditionals: `score = 85
if score >= 90:
    print(True)
elif score >= 70:
    print(score)
else:
    print(False)`,

    while_loop: `n = 5
total = 0
while n > 0:
    total = total + n
    n = n - 1
print(total)`,

    for_loop: `nums = [10, 20, 30, 40, 50]
total = 0
for x in nums:
    total = total + x
print(total)`,

    do_while: `i = 1
do:
    print(i)
    i = i + 1
while i <= 3`,

    arrays: `arr = [1, 2, 3, 4, 5]
print(len(arr))
print(arr[0])
arr[2] = 99
print(arr[2])
for item in range(5):
    print(item)`,

    operators: `a = 7
b = 2
print(a // b)
print(a % b)
print(a ** b)
flag = a > b
if flag:
    print(True)
elif a == b:
    print(False)
else:
    print(a - b)`,
};

// ── Line Numbers ──────────────────────────────────────────────────
function updateLineNumbers() {
    const lines = editor.value.split('\n');
    const count = Math.max(lines.length, 1);
    let html = '';
    for (let i = 1; i <= count; i++) html += i + '\n';
    lineNumbers.textContent = html;
}

editor.addEventListener('input', updateLineNumbers);
editor.addEventListener('scroll', () => { lineNumbers.scrollTop = editor.scrollTop; });
updateLineNumbers();

// ── Tab key support ───────────────────────────────────────────────
editor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        const s = editor.selectionStart, end = editor.selectionEnd;
        editor.value = editor.value.substring(0, s) + '    ' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = s + 4;
        updateLineNumbers();
    }
});

// ── Snippet Buttons ───────────────────────────────────────────────
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

// ── Status Helpers ────────────────────────────────────────────────
function setStatus(state, text) {
    statusDot.className = 'status-dot' + (state !== 'ready' ? ' ' + state : '');
    statusText.textContent = text;
}

// ── Badge Helpers ─────────────────────────────────────────────────
function setBadge(el, status, text) {
    el.className = 'stage-badge ' + status;
    el.textContent = text;
}

function flashPanel(panel, type) {
    panel.classList.remove('flash-pass', 'flash-fail');
    void panel.offsetWidth; // reflow
    panel.classList.add(type === 'pass' ? 'flash-pass' : 'flash-fail');
    setTimeout(() => panel.classList.remove('flash-pass', 'flash-fail'), 600);
}

// ── HTML escape ───────────────────────────────────────────────────
function esc(text) {
    const d = document.createElement('div');
    d.textContent = String(text);
    return d.innerHTML;
}

// ── Placeholder helper ────────────────────────────────────────────
function placeholder(icon, text) {
    return `<div class="stage-placeholder"><span class="ph-icon">${icon}</span><span>${esc(text)}</span></div>`;
}

// ── Reset all panels ──────────────────────────────────────────────
function resetPanels() {
    const ph = (icon, txt) => placeholder(icon, txt);
    bodyLexer.innerHTML    = ph('⬡', 'Token stream will appear here');
    bodySyntax.innerHTML   = ph('⬡', 'Parse result will appear here');
    bodySemantic.innerHTML = ph('⬡', 'Scope table & type info will appear here');
    bodyValidator.innerHTML= ph('⬡', 'Validation results will appear here');
    bodyExecutor.innerHTML = ph('▶', 'Program output will appear here');
    astBody.innerHTML      = ph('🌳', 'AST will appear here after compile');

    ['badgeLexer','badgeSyntax','badgeSemantic','badgeValidator','badgeExecutor'].forEach(id => {
        const el = document.getElementById('badge-' + id.replace('badge','').toLowerCase());
        if (el) { el.className = 'stage-badge'; el.textContent = '—'; }
    });
    setBadge(badgeLexer,    '', '—');
    setBadge(badgeSyntax,   '', '—');
    setBadge(badgeSemantic, '', '—');
    setBadge(badgeValidator,'', '—');
    setBadge(badgeExecutor, '', '—');
}

// ═══════════════════════════════════════════════════════════════════
// ── Stage 1: LEXER panel renderer ────────────────────────────────
// ═══════════════════════════════════════════════════════════════════

// Map token types to CSS class + display label
const TOKEN_DISPLAY = {
    'INT':     { cls: 'tok-INT',     label: 'INT' },
    'FLOAT':   { cls: 'tok-FLOAT',   label: 'FLOAT' },
    'NAME':    { cls: 'tok-NAME',    label: 'NAME' },
    'COMP_OP': { cls: 'tok-COMP_OP', label: 'COMP_OP' },
    'CHAR':    { cls: 'tok-CHAR',    label: 'CHAR' },
    'LPAR':    { cls: 'tok-DELIM',   label: 'DELIM' },
    'RPAR':    { cls: 'tok-DELIM',   label: 'DELIM' },
    'LSQB':    { cls: 'tok-DELIM',   label: 'DELIM' },
    'RSQB':    { cls: 'tok-DELIM',   label: 'DELIM' },
    'LBRACE':  { cls: 'tok-DELIM',   label: 'DELIM' },
    'RBRACE':  { cls: 'tok-DELIM',   label: 'DELIM' },
};

const KEYWORDS = new Set(['if','elif','else','while','for','in','do',
                           'print','and','or','not','True','False','range','len']);

function getTokenDisplay(tok) {
    if (TOKEN_DISPLAY[tok.type]) return TOKEN_DISPLAY[tok.type];
    // Classify keywords vs operators
    if (tok.type === 'NAME') {
        if (KEYWORDS.has(tok.lexeme)) return { cls: 'tok-KEYWORD', label: 'KEYWORD' };
        if (tok.lexeme === 'True' || tok.lexeme === 'False') return { cls: 'tok-BOOL', label: 'BOOL' };
        return { cls: 'tok-NAME', label: 'NAME' };
    }
    // Single-char operators and punctuation
    if (['+','-','*','/','^','=','<','>','!','%','&','|',':',',','[',']','(',')','{','}'].includes(tok.lexeme)) {
        return { cls: 'tok-OP', label: 'OP' };
    }
    return { cls: 'tok-OTHER', label: tok.type || 'TK' };
}

function renderLexer(tokens) {
    if (!tokens || tokens.length === 0) {
        bodyLexer.innerHTML = placeholder('⬡', 'No tokens produced');
        setBadge(badgeLexer, 'warn', '0 tokens');
        return;
    }

    let html = `<table class="token-table">
        <thead><tr>
            <th>#</th><th>Type</th><th>Lexeme</th><th>Line</th>
        </tr></thead><tbody>`;

    tokens.forEach((tok, i) => {
        const disp = getTokenDisplay(tok);
        html += `<tr>
            <td class="tok-line">${i + 1}</td>
            <td><span class="tok-type ${disp.cls}">${esc(disp.label)}</span></td>
            <td class="tok-lexeme" title="${esc(tok.lexeme)}">${esc(tok.lexeme)}</td>
            <td class="tok-line">${tok.line || '—'}</td>
        </tr>`;
    });

    html += '</tbody></table>';
    bodyLexer.innerHTML = html;
    setBadge(badgeLexer, 'pass', `${tokens.length} tokens`);
    flashPanel(panelLexer, 'pass');
}

// ═══════════════════════════════════════════════════════════════════
// ── Stage 2: SYNTAX ANALYSER panel renderer ───────────────────────
// ═══════════════════════════════════════════════════════════════════

function renderSyntax(syntaxErrors) {
    if (!syntaxErrors || syntaxErrors.length === 0) {
        bodySyntax.innerHTML = `<div class="result-success">✓ Parse successful — grammar rules satisfied</div>`;
        setBadge(badgeSyntax, 'pass', '✓ Passed');
        flashPanel(panelSyntax, 'pass');
    } else {
        let html = '';
        syntaxErrors.forEach(err => {
            html += `<div class="result-error">${esc(err)}</div>`;
        });
        bodySyntax.innerHTML = html;
        setBadge(badgeSyntax, 'fail', '✗ Error');
        flashPanel(panelSyntax, 'fail');
    }
}

// ═══════════════════════════════════════════════════════════════════
// ── Stage 3: SEMANTIC ANALYSER panel renderer ─────────────────────
// ═══════════════════════════════════════════════════════════════════

function renderSemantic(semanticErrors, semanticInfo, syntaxFailed) {
    if (syntaxFailed) {
        bodySemantic.innerHTML = placeholder('⬡', 'Skipped — syntax errors must be resolved first');
        setBadge(badgeSemantic, '', '—');
        return;
    }

    let html = '';

    // Scope table
    const symbolTable = (semanticInfo && semanticInfo.symbol_table) ? semanticInfo.symbol_table : {};
    const entries = Object.entries(symbolTable);

    if (entries.length > 0) {
        html += `<div style="font-family:var(--font-sans);font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.06em;font-weight:700;margin-bottom:4px;">Symbol Table</div>`;
        html += `<table class="scope-table"><thead><tr><th>Variable</th><th>Type</th></tr></thead><tbody>`;
        entries.forEach(([name, type]) => {
            html += `<tr>
                <td class="scope-name">${esc(name)}</td>
                <td><span class="type-badge type-${esc(type)}">${esc(type)}</span></td>
            </tr>`;
        });
        html += '</tbody></table>';
    }

    if (semanticErrors && semanticErrors.length > 0) {
        semanticErrors.forEach(err => {
            html += `<div class="result-error" style="margin-top:6px">${esc(err)}</div>`;
        });
        bodySemantic.innerHTML = html || placeholder('⬡', 'No info');
        setBadge(badgeSemantic, 'fail', '✗ Error');
        flashPanel(panelSemantic, 'fail');
    } else {
        if (entries.length === 0) {
            html += `<div class="result-success">✓ No semantic errors detected</div>`;
        } else {
            html += `<div class="result-success" style="margin-top:6px">✓ Semantics OK</div>`;
        }
        bodySemantic.innerHTML = html;
        setBadge(badgeSemantic, 'pass', '✓ Passed');
        flashPanel(panelSemantic, 'pass');
    }
}

// ═══════════════════════════════════════════════════════════════════
// ── Stage 4: VALIDATOR panel renderer ────────────────────────────
// ═══════════════════════════════════════════════════════════════════

function renderValidator(validationData) {
    const checks = (validationData && validationData.checks) ? validationData.checks : [];

    if (checks.length === 0) {
        bodyValidator.innerHTML = placeholder('⬡', 'No validation data');
        setBadge(badgeValidator, '', '—');
        return;
    }

    const icons = { pass: '✓', fail: '✗', warn: '⚠' };
    const colors = { pass: 'var(--green)', fail: 'var(--red)', warn: 'var(--yellow)' };

    let html = '';
    let hasFail = false, hasWarn = false;

    checks.forEach(check => {
        const icon = icons[check.status] || '•';
        const color = colors[check.status] || 'var(--text-muted)';
        if (check.status === 'fail') hasFail = true;
        if (check.status === 'warn') hasWarn = true;
        html += `<div class="check-row">
            <span class="check-icon" style="color:${color}">${icon}</span>
            <div>
                <div class="check-name" style="color:${color}">${esc(check.name)}</div>
                <div class="check-detail">${esc(check.details || '')}</div>
            </div>
        </div>`;
    });

    bodyValidator.innerHTML = html;

    if (hasFail) {
        setBadge(badgeValidator, 'fail', '✗ Issues');
        flashPanel(panelValidator, 'fail');
    } else if (hasWarn) {
        setBadge(badgeValidator, 'warn', '⚠ Warnings');
    } else {
        setBadge(badgeValidator, 'pass', '✓ Valid');
        flashPanel(panelValidator, 'pass');
    }
}

// ═══════════════════════════════════════════════════════════════════
// ── Stage 5: EXECUTOR panel renderer ─────────────────────────────
// ═══════════════════════════════════════════════════════════════════

function renderExecutor(output, runtimeError, syntaxFailed, semanticFailed, elapsed) {
    if (syntaxFailed) {
        bodyExecutor.innerHTML = placeholder('▶', 'Skipped — fix syntax errors first');
        setBadge(badgeExecutor, '', '—');
        return;
    }
    if (semanticFailed) {
        bodyExecutor.innerHTML = placeholder('▶', 'Skipped — fix semantic errors first');
        setBadge(badgeExecutor, '', '—');
        return;
    }

    if (runtimeError) {
        bodyExecutor.innerHTML = `<div class="result-error">${esc(runtimeError)}</div>`;
        setBadge(badgeExecutor, 'fail', '✗ Runtime Error');
        flashPanel(panelExecutor, 'fail');
        return;
    }

    let html = '';
    if (output && output.trim()) {
        const lines = output.split('\n').filter(l => l !== '');
        lines.forEach(line => {
            html += `<div class="exec-line"><span class="exec-prompt">›</span>${esc(line)}</div>`;
        });
    } else {
        html += `<div class="exec-no-output">(no output)</div>`;
    }

    if (elapsed !== undefined) {
        html += `<div class="exec-timing">Completed in ${elapsed}ms</div>`;
    }

    bodyExecutor.innerHTML = html;
    setBadge(badgeExecutor, 'pass', '✓ Done');
    flashPanel(panelExecutor, 'pass');
}

// ═══════════════════════════════════════════════════════════════════
// ── AST Tree renderer (branching tree with connector lines) ───────
// ═══════════════════════════════════════════════════════════════════

// Classify AST node types into colour categories
const AST_CATEGORIES = {
    Program:          'program',
    Assignment:       'statement',
    IndexAssignment:  'statement',
    PrintStatement:   'statement',
    IfStatement:      'statement',
    ElifClause:       'clause',
    ElseClause:       'clause',
    WhileStatement:   'loop',
    ForStatement:     'loop',
    DoWhileStatement: 'loop',
    BinaryOp:         'operator',
    UnaryOp:          'operator',
    Comparison:       'operator',
    BooleanOp:        'operator',
    NotOp:            'operator',
    IntLiteral:       'literal',
    FloatLiteral:     'literal',
    CharLiteral:      'literal',
    BoolLiteral:      'literal',
    Variable:         'variable',
    ArrayLiteral:     'array',
    IndexAccess:      'array',
    RangeExpression:  'builtin',
    LenExpression:    'builtin',
};

const LEAF_TYPES = new Set(['IntLiteral','FloatLiteral','CharLiteral','BoolLiteral','Variable']);

/**
 * Collect the child entries of a node — each is { edgeLabel, childNode }
 * where edgeLabel is the field name (e.g. "left", "condition", "body[0]").
 * Also returns scalar fields for inline display.
 */
function collectNodeParts(node) {
    const children = [];
    const scalars  = [];

    for (const [key, val] of Object.entries(node)) {
        if (key === '_type') continue;
        if (val === null || val === undefined) continue;

        if (typeof val === 'object' && !Array.isArray(val) && val._type) {
            // Single AST child
            children.push({ edgeLabel: key, childNode: val });
        } else if (Array.isArray(val)) {
            // Array of children
            val.forEach((item, idx) => {
                if (item && typeof item === 'object' && item._type) {
                    children.push({ edgeLabel: `${key}[${idx}]`, childNode: item });
                }
            });
        } else {
            scalars.push({ key, val });
        }
    }
    return { children, scalars };
}

/**
 * Build a single <li> element for an AST node, recursively attaching
 * sub-<ul> children. The CSS draws branch connector lines via pseudo-elements.
 *
 * @param {object}  node       — the JSON AST node (has _type)
 * @param {string|null} edgeLabel — label for the branch leading to this node
 */
function buildTreeNode(node, edgeLabel) {
    if (!node || typeof node !== 'object' || !node._type) return null;

    const typeName  = node._type;
    const category  = AST_CATEGORIES[typeName] || 'statement';
    const isLeaf    = LEAF_TYPES.has(typeName);
    const { children, scalars } = collectNodeParts(node);
    const hasChildren = children.length > 0;

    // Build inline scalar annotation
    let scalarHtml = '';
    if (scalars.length > 0 && scalars.length <= 3) {
        const parts = scalars.map(s => `${s.key}=<span>${esc(JSON.stringify(s.val))}</span>`);
        scalarHtml = `<span class="ast-node-fields">${parts.join(' ')}</span>`;
    }

    // Build the edge label prefix (e.g. "left: ", "condition: ")
    const edgeHtml = edgeLabel
        ? `<span class="ast-edge-label">${esc(edgeLabel)}:</span>`
        : '';

    // Toggle glyph
    const toggleCls  = hasChildren ? 'has-children' : 'leaf-dot';
    const toggleChar = hasChildren ? '▼' : '●';

    // Create <li>
    const li = document.createElement('li');

    // Node row
    const row = document.createElement('div');
    row.className = 'ast-node-row';
    row.innerHTML = `${edgeHtml}<span class="ast-toggle ${toggleCls}">${toggleChar}</span><span class="ast-node-name ast-cat-${category}">${esc(typeName)}</span>${scalarHtml}`;
    li.appendChild(row);

    // Recursively build children
    if (hasChildren) {
        const ul = document.createElement('ul');
        ul.className = 'ast-children';

        children.forEach(({ edgeLabel: label, childNode }) => {
            const childLi = buildTreeNode(childNode, label);
            if (childLi) ul.appendChild(childLi);
        });

        li.appendChild(ul);

        // Click to collapse/expand
        row.addEventListener('click', () => {
            const collapsed = ul.classList.toggle('collapsed');
            const tog = row.querySelector('.ast-toggle');
            if (tog) tog.textContent = collapsed ? '▶' : '▼';
        });
    }

    return li;
}

function renderAST(astJson) {
    if (!astJson || typeof astJson !== 'object') {
        astBody.innerHTML = placeholder('🌳', 'AST not available');
        return;
    }

    const rootLi = buildTreeNode(astJson, null);
    if (!rootLi) {
        astBody.innerHTML = placeholder('🌳', 'Could not render AST');
        return;
    }

    const ul = document.createElement('ul');
    ul.className = 'ast-tree ast-root';          // ast-root hides branch on root
    ul.appendChild(rootLi);
    astBody.innerHTML = '';
    astBody.appendChild(ul);
}

// Expand / Collapse all
btnExpandAll.addEventListener('click', () => {
    astBody.querySelectorAll('.ast-children').forEach(ul => ul.classList.remove('collapsed'));
    astBody.querySelectorAll('.ast-toggle').forEach(el => {
        if (el.classList.contains('has-children')) el.textContent = '▼';
    });
});

btnCollapseAll.addEventListener('click', () => {
    astBody.querySelectorAll('.ast-children').forEach(ul => ul.classList.add('collapsed'));
    astBody.querySelectorAll('.ast-toggle').forEach(el => {
        if (el.classList.contains('has-children')) el.textContent = '▶';
    });
});

// ═══════════════════════════════════════════════════════════════════
// ── Main Run / Compile ────────────────────────────────────────────
// ═══════════════════════════════════════════════════════════════════

async function runCode() {
    const code = editor.value;

    if (!code.trim()) {
        resetPanels();
        bodySyntax.innerHTML = `<div class="result-error">No code to compile.</div>`;
        return;
    }

    setStatus('running', 'Compiling...');
    btnRun.classList.add('running');
    resetPanels();

    const startTime = performance.now();

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
        });

        const data = await response.json();
        const elapsed = Math.round(performance.now() - startTime);

        // Determine which stage failed
        const syntaxFailed   = !!(data.syntax_errors && data.syntax_errors.length > 0);
        const semanticFailed = !!(data.semantic_errors && data.semantic_errors.length > 0);
        const runtimeFailed  = !data.success && !syntaxFailed && !semanticFailed;

        // 1. Lexer panel — always render if we have tokens
        renderLexer(data.tokens || []);

        // 2. Syntax panel
        renderSyntax(data.syntax_errors || []);

        // 3. Semantic panel
        renderSemantic(data.semantic_errors || [], data.semantic_info, syntaxFailed);

        // 4. Validator panel
        renderValidator(data.validation);

        // 5. Executor panel
        const runtimeErrMsg = runtimeFailed && data.error ? data.error.message : null;
        renderExecutor(data.output, runtimeErrMsg, syntaxFailed, semanticFailed, elapsed);

        // 6. AST tree
        renderAST(data.ast);

        // Status indicator
        if (data.success) {
            setStatus('ready', `✓ Done (${elapsed}ms)`);
        } else {
            setStatus('error', data.error ? data.error.type : 'Error');
            setTimeout(() => setStatus('ready', 'Ready'), 4000);
        }

    } catch (err) {
        setStatus('error', 'Connection Error');
        bodySyntax.innerHTML = `<div class="result-error">Failed to connect to the interpreter server.\nMake sure the server is running: python web_app.py</div>`;
        setBadge(badgeSyntax, 'fail', '✗ Error');
        setTimeout(() => setStatus('ready', 'Ready'), 4000);
    } finally {
        btnRun.classList.remove('running');
    }
}

// ── Event Bindings ────────────────────────────────────────────────
btnRun.addEventListener('click', runCode);

btnClear.addEventListener('click', () => {
    editor.value = '';
    updateLineNumbers();
    resetPanels();
    editor.focus();
    setStatus('ready', 'Ready');
});

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        runCode();
    }
});
