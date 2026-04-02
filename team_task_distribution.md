# Team Task Distribution — File-Level Ownership

> Each member owns **specific files** they can present as "I wrote this." Every member has at least one **core compiler file** plus supporting files.

---

## All Project Files (14 total)

```
Mini Python Interpreter/
├── requirements.txt            ← Member 2
├── README.md                   ← Member 1
│
├── src/
│   ├── __init__.py             ← Member 3
│   ├── __main__.py             ← Member 3
│   ├── grammar.py              ← Member 1  ⚙️ COMPILER
│   ├── ast_nodes.py            ← Member 2  ⚙️ COMPILER
│   ├── lexer_parser.py         ← Member 2  ⚙️ COMPILER
│   ├── semantic_analyzer.py    ← Member 3  ⚙️ COMPILER
│   ├── evaluator.py            ← Member 4  ⚙️ COMPILER
│   └── cli.py                  ← Member 3  ⚙️ COMPILER
│
├── web/
│   ├── templates/index.html    ← Member 4
│   └── static/
│       ├── style.css           ← Member 4
│       └── app.js              ← Member 4
│
├── web_app.py                  ← Member 4
├── examples/demo.mpy           ← Member 1
│
└── tests/
    ├── __init__.py             ← Member 4
    └── test_interpreter.py     ← Member 4
```

---

## 👤 Member 1 — Grammar Design & Documentation

> *"I designed the language grammar and wrote the project documentation."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/grammar.py`** | ⚙️ Compiler Core | Lark EBNF grammar — defines the entire mini-Python language syntax: operator precedence, statement rules, terminal patterns |
| `README.md` | Documentation | Project overview, architecture diagram, setup guide, debugging guide |
| `examples/demo.mpy` | Example | Demo program showcasing all language features |

### What they should know:

- How EBNF grammar rules define the language
- Why `arith_expr → term → factor → power → atom` encodes precedence
- What LALR parsing is and why Lark uses it
- How `INDENT` / `DEDENT` tokens handle Python-style indentation
- How `CHAR`, `INT`, `FLOAT`, `NAME` terminals are defined

### Lines of code: ~105 (grammar) + ~280 (README) = **~385 lines**

### Can present / demo:

```python
# "Here's how the grammar defines operator precedence"
# Show grammar.py, explain how lower rules = lower precedence
# arith_expr (+ -) → term (* / // %) → factor (unary) → power (**) → atom
```

---

## 👤 Member 2 — AST Design & Parser Frontend

> *"I designed the AST data structures and built the parser that converts source code into AST nodes."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/ast_nodes.py`** | ⚙️ Compiler Core | 16 frozen dataclass AST nodes — the data contract between all compiler layers |
| **`src/lexer_parser.py`** | ⚙️ Compiler Core | `MiniPythonIndenter` for indent/dedent, `ASTBuilder` transformer (18 methods), `parse()` public API |
| `requirements.txt` | Config | Project dependencies (lark, pytest, flask) |

### What they should know:

- Why AST nodes are **frozen dataclasses** (immutable, auto `__eq__`, type-safe)
- The full AST node hierarchy (16 nodes)
- How the `ASTBuilder` Lark `Transformer` works (bottom-up traversal)
- How `MiniPythonIndenter` generates `INDENT`/`DEDENT` tokens
- What `propagate_positions=True` does (line/col info for error messages)

### Lines of code: ~150 (ast_nodes) + ~200 (lexer_parser) = **~350 lines**

### Can present / demo:

```python
from src.lexer_parser import parse
ast = parse("x = 2 + 3 * 4\n")
print(ast)
# Show the AST structure: Program → Assignment → BinaryOp(+, 2, BinaryOp(*, 3, 4))
# Explain how 3*4 binds tighter than 2+... because of the grammar hierarchy
```

---

## 👤 Member 3 — Semantic Analysis & CLI Interface

> *"I built the type checker with the symbol table and the command-line interface that ties everything together."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/semantic_analyzer.py`** | ⚙️ Compiler Core | Symbol table, type inference, type-checking rules for all operators, semantic error reporting |
| **`src/cli.py`** | ⚙️ Compiler Core | Pipeline wiring (Parse → Analyze → Evaluate), REPL with state persistence, file execution mode, ANSI color-coded errors |
| `src/__init__.py` | Package | Package init with module overview |
| `src/__main__.py` | Entry point | `python -m src` entry point |

### TODO exercises to complete:

| # | Method | Exercise |
|---|---|---|
| 1 | `_check_binary_op` | Float promotion for modulo `%` |
| 2 | `_check_binary_op` | Float promotion for floor division `//` |
| 3 | `_check_binary_op` | Mixed type rules for power `**` |
| 4 | `_check_binary_op` | Error guard on `char` operands |
| 5 | `_check_binary_op` | Error guard on `bool` operands |
| 6 | `_check_comparison` | Bool-to-bool equality (`==`, `!=`) |
| 7 | `_check_comparison` | Explicit cross-type error messages |

### What they should know:

- How the **symbol table** tracks variable names → types
- How **type inference** works (e.g., `x = 1 + 2.5` → `x` is `float`)
- How **int → float promotion** works on reassignment
- How the **REPL persists state** across inputs (symbol table + evaluator)
- The 3 error types and how the CLI color-codes them by stage

### Lines of code: ~470 (semantic_analyzer) + ~195 (cli) = **~665 lines**

### Can present / demo:

```python
from src.lexer_parser import parse
from src.semantic_analyzer import SemanticAnalyzer

ast = parse("x = 42\ny = x + 1.5\n")
analyzer = SemanticAnalyzer()
analyzer.analyze(ast)
print(analyzer.symbol_table)
# {'x': 'int', 'y': 'float'}  — shows promotion
```

```bash
# Also demo the CLI REPL
python -m src
>>> x = 10
>>> print(x + 5)
15
```

---

## 👤 Member 4 — Evaluator, Web IDE & Testing

> *"I built the execution engine using the Visitor Pattern, the web-based IDE, and the complete test suite."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/evaluator.py`** | ⚙️ Compiler Core | Visitor-pattern AST traversal, variable store, runtime execution, truthiness logic |
| `web_app.py` | Web Backend | Flask server, `/api/run` endpoint, AST preview generation |
| `web/templates/index.html` | Web Frontend | IDE layout with code editor, tabs, snippets |
| `web/static/style.css` | Web Frontend | Dark glassmorphism design system |
| `web/static/app.js` | Web Frontend | Editor logic, API calls, result rendering |
| `tests/test_interpreter.py` | Testing | 85 tests across 5 classes (parser, analyzer, evaluator, integration, edge cases) |
| `tests/__init__.py` | Package | Test package init |

### TODO exercises to complete:

| # | Method | Exercise |
|---|---|---|
| 1 | `_eval_binary_op` | Floor division `//` with zero guard |
| 2 | `_eval_binary_op` | Modulo `%` with zero guard |
| 3 | `_eval_binary_op` | Exponentiation `**` |
| 4 | `_eval_comparison` | Less than `<` |
| 5 | `_eval_comparison` | Greater than `>` |
| 6 | `_eval_comparison` | Less or equal `<=` |
| 7 | `_eval_comparison` | Greater or equal `>=` |
| 8 | `_eval_boolean_op` | Short-circuit `and` / `or` |
| 9 | `_exec_if` | `elif` clause evaluation |
| 10 | `_exec_if` | `else` clause fallback |

### What they should know:

- The **Visitor Pattern** — how `_eval` dispatches to `_eval_*` methods
- Difference between **symbol table** (types, analysis-time) vs. **variable store** (values, runtime)
- How `_is_truthy` determines truthiness (matching Python semantics)
- How the **Web IDE** sends code to `/api/run` and displays results
- How `@pytest.mark.xfail` works and when to remove it

### Lines of code: ~300 (evaluator) + ~170 (web_app) + ~120 (HTML) + ~530 (CSS) + ~260 (JS) + ~430 (tests) = **~1810 lines**

### Can present / demo:

```python
from src.evaluator import Evaluator
from src.lexer_parser import parse

ev = Evaluator()
ast = parse("x = 10\nprint(x * 3 + 2)\n")
output = ev.execute(ast)
print(output)        # "32\n"
print(ev.variables)  # {'x': 10}
```

```bash
# Also demo the Web IDE
python web_app.py
# → Open http://localhost:5000
```

---

## 📊 Summary Table

| Member | Compiler File(s) | Supporting File(s) | TODOs | Total Lines |
|---|---|---|---|---|
| **Member 1** | `grammar.py` | `README.md`, `demo.mpy` | 0 | ~385 |
| **Member 2** | `ast_nodes.py`, `lexer_parser.py` | `requirements.txt` | 0 | ~350 |
| **Member 3** | `semantic_analyzer.py`, `cli.py` | `__init__.py`, `__main__.py` | 7 | ~665 |
| **Member 4** | `evaluator.py` | `web_app.py`, `web/`, `tests/` | 10 | ~1810 |

---

## 🎯 Presentation Order

| # | Who | Duration | What they present |
|---|---|---|---|
| 1 | **Member 1** | 3 min | Language design: grammar rules, operator precedence, EBNF notation |
| 2 | **Member 2** | 3 min | AST design: node hierarchy, parser transformer, how source becomes a tree |
| 3 | **Member 3** | 4 min | Type system: symbol table, type inference, promotion rules, CLI demo |
| 4 | **Member 4** | 4 min | Execution: Visitor Pattern, runtime evaluation, Web IDE demo |
| 5 | **All** | 4 min | End-to-end live demo + test suite run + Q&A |

> [!TIP]
> **Suggested talking point:** *"Each of us built a separate module, but they all communicate through the AST — Member 2's parser produces it, Member 3's analyzer validates it, and Member 4's evaluator executes it. Member 1's grammar defines what's legal in the first place."*

---

## ✅ Pre-Presentation Checklist

- [ ] **Member 3**: Complete all 7 semantic analyzer TODOs
- [ ] **Member 4**: Complete all 10 evaluator TODOs
- [ ] **Member 4**: Remove `@pytest.mark.xfail` from all completed tests
- [ ] **All**: Run `pytest tests/ -v` → **85 passed, 0 failed**
- [ ] **All**: Each person can explain their files line-by-line if asked
- [ ] **All**: Each person can trace `print(1 + 2)` through their module
- [ ] **Member 3**: Demo the CLI REPL live
- [ ] **Member 4**: Demo the Web IDE live
