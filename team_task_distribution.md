# Team Task Distribution — File-Level Ownership

> Each member owns **specific files** they can present as "I wrote this." Every member has at least one **core compiler file** plus supporting files.

---

## All Project Files (15 total)

```
Mini Python Interpreter/
├── requirements.txt            ← Member 2
├── README.md                   ← Member 1
├── team_task_distribution.md   ← Member 1
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

> *"I designed the language grammar — including loops and arrays — and wrote the project documentation."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/grammar.py`** | ⚙️ Compiler Core | Lark EBNF grammar — defines the entire mini-Python language syntax: operator precedence, statement rules, terminal patterns, loop constructs (`while`, `for-in`, `do-while`), array literals, indexing, `range()`, `len()` |
| `README.md` | Documentation | Project overview, 5-stage architecture diagram, feature table, Compiler Visualizer IDE guide, setup/debugging instructions |
| `team_task_distribution.md` | Documentation | Team member file ownership and presentation plan |
| `examples/demo.mpy` | Example | Demo program showcasing all language features |

### What they should know:

- How EBNF grammar rules define the language
- Why `arith_expr → term → factor → power → postfix → atom` encodes precedence
- What LALR parsing is and why Lark uses it
- How `INDENT` / `DEDENT` tokens handle Python-style indentation
- How `CHAR`, `INT`, `FLOAT`, `NAME` terminals are defined
- How the grammar rules for `while_statement`, `for_statement`, `do_while_statement` work
- How `postfix` rule enables chained indexing (`arr[i]`)
- How `array_literal`, `range_expr`, and `len_expr` are parsed as atoms

### Lines of code: ~135 (grammar) + ~390 (README) + ~275 (task dist) = **~800 lines**

### Can present / demo:

```python
# "Here's how the grammar defines operator precedence"
# Show grammar.py, explain how lower rules = lower precedence
# arith_expr (+ -) → term (* / // %) → factor (unary) → power (**) → postfix ([]) → atom

# "Here's how loops are defined"
# while_statement: "while" expression ":" block
# for_statement: "for" NAME "in" expression ":" block
# do_while_statement: "do" ":" block "while" expression

# "Here's how arrays are defined"
# array_literal: "[" expression ("," expression)* "]"
# index_access: postfix "[" expression "]"
# range_expr: "range" "(" expression ("," expression)* ")"
```

---

## 👤 Member 2 — AST Design & Parser Frontend

> *"I designed the AST data structures — including nodes for loops and arrays — and built the parser that converts source code into AST nodes."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/ast_nodes.py`** | ⚙️ Compiler Core | 24 frozen dataclass AST nodes — the data contract between all compiler layers. Includes nodes for loops (`WhileStatement`, `ForStatement`, `DoWhileStatement`) and arrays (`ArrayLiteral`, `IndexAccess`, `IndexAssignment`, `RangeExpression`, `LenExpression`) |
| **`src/lexer_parser.py`** | ⚙️ Compiler Core | `MiniPythonIndenter` for indent/dedent, `ASTBuilder` transformer (26 methods), `parse()` and `tokenize()` public APIs |
| `requirements.txt` | Config | Project dependencies (lark, pytest, flask) |

### What they should know:

- Why AST nodes are **frozen dataclasses** (immutable, auto `__eq__`, type-safe)
- The full AST node hierarchy (24 nodes across 6 categories):
  - **Literals** (5): IntLiteral, FloatLiteral, CharLiteral, BoolLiteral, Variable
  - **Operators** (5): BinaryOp, UnaryOp, Comparison, BooleanOp, NotOp
  - **Statements** (4): Assignment, IndexAssignment, PrintStatement, IfStatement
  - **Clauses** (2): ElifClause, ElseClause
  - **Loops** (3): WhileStatement, ForStatement, DoWhileStatement
  - **Arrays/Builtins** (4): ArrayLiteral, IndexAccess, RangeExpression, LenExpression
  - **Root** (1): Program
- How the `ASTBuilder` Lark `Transformer` works (bottom-up traversal)
- How `MiniPythonIndenter` generates `INDENT`/`DEDENT` tokens
- How `tokenize()` extracts a token stream for the visualizer frontend
- What `propagate_positions=True` does (line/col info for error messages)

### Lines of code: ~176 (ast_nodes) + ~270 (lexer_parser) = **~446 lines**

### Can present / demo:

```python
from src.lexer_parser import parse, tokenize

ast = parse("x = [1, 2, 3]\nfor i in range(3):\n    print(x[i])\n")
print(ast)
# Show the AST structure: Program → Assignment(arr) + ForStatement(i, range, body)
# Explain how ArrayLiteral and IndexAccess nodes are constructed

tokens = tokenize("x = 5\nprint(x)")
print(tokens)
# [{'type': 'NAME', 'lexeme': 'x', 'line': 1}, {'type': 'OP', ...}, ...]
```

---

## 👤 Member 3 — Semantic Analysis & CLI Interface

> *"I built the type checker with the symbol table — handling arrays and loops — and the command-line interface that ties everything together."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/semantic_analyzer.py`** | ⚙️ Compiler Core | Symbol table, type inference (int/float/char/bool/array/any), type-checking rules for all operators and constructs, semantic error reporting |
| **`src/cli.py`** | ⚙️ Compiler Core | Pipeline wiring (Parse → Analyze → Evaluate), REPL with state persistence, file execution mode, ANSI color-coded errors |
| `src/__init__.py` | Package | Package init with module overview |
| `src/__main__.py` | Entry point | `python -m src` entry point |

### What they should know:

- How the **symbol table** tracks variable names → types (`int`, `float`, `char`, `bool`, `array`, `any`)
- How **type inference** works (e.g., `x = 1 + 2.5` → `x` is `float`)
- How **int → float promotion** works on reassignment
- How `array` type is inferred for array literals and `range()`
- How `any` type is used for index-access results and `for` loop variables (element type unknown statically)
- How the loop condition type is validated (must be bool-compatible)
- How `len()` is type-checked to require an `array` argument and return `int`
- How **index assignment** is validated (variable must exist and be `array` type)
- How the **REPL persists state** across inputs (symbol table + evaluator)
- The 3 error types and how the CLI color-codes them by stage

### Lines of code: ~330 (semantic_analyzer) + ~195 (cli) = **~525 lines**

### Can present / demo:

```python
from src.lexer_parser import parse
from src.semantic_analyzer import SemanticAnalyzer

ast = parse("arr = [1, 2, 3]\ntotal = 0\nfor x in arr:\n    total = total + x\n")
analyzer = SemanticAnalyzer()
analyzer.analyze(ast)
print(analyzer.symbol_table)
# {'arr': 'array', 'total': 'int', 'x': 'any'}
# — arr is array, total is int, x is any (element type unknown)
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

> *"I built the execution engine using the Visitor Pattern — including loops and arrays — the Compiler Visualizer IDE, and the complete test suite."*

### Files owned:

| File | Type | What it does |
|---|---|---|
| **`src/evaluator.py`** | ⚙️ Compiler Core | Visitor-pattern AST traversal, variable store, runtime execution of all constructs (arithmetic, conditionals, loops, arrays), truthiness logic, infinite-loop protection |
| `web_app.py` | Web Backend | Flask server, enriched `/api/run` endpoint returning tokens, AST JSON, semantic info, validation checks, output |
| `web/templates/index.html` | Web Frontend | 3-column IDE layout: editor, 5 pipeline panels, AST tree |
| `web/static/style.css` | Web Frontend | Dark glassmorphism design system, stage panel accents, branching tree CSS |
| `web/static/app.js` | Web Frontend | Pipeline orchestration, token table renderer, AST branching tree builder, expand/collapse logic |
| `tests/test_interpreter.py` | Testing | 85 tests across 5 classes (parser, analyzer, evaluator, integration, edge cases) |
| `tests/__init__.py` | Package | Test package init |

### What they should know:

- The **Visitor Pattern** — how `_eval` dispatches to `_eval_*` methods based on node type
- Difference between **symbol table** (types, analysis-time) vs. **variable store** (values, runtime)
- How `_is_truthy` determines truthiness (matching Python semantics): bool, int/float≠0, non-empty str/list
- How **`while` loops** execute with `MAX_ITERATIONS` infinite-loop protection
- How **`for` loops** iterate over arrays/ranges, setting the loop variable each iteration
- How **`do-while` loops** execute the body before checking the condition
- How **arrays** are runtime `list` values: literals, index access (with bounds checking), index assignment
- How **`range()`** produces a Python `list` and supports 1–3 arguments
- How **`len()`** operates on list values at runtime
- How the **enriched API** returns structured JSON with tokens, AST, semantic info, validation, and output
- How the **3-column visualizer** renders 5 pipeline panels + a branching AST tree
- How `@pytest.mark.xfail` works and when to remove it

### Lines of code: ~310 (evaluator) + ~250 (web_app) + ~200 (HTML) + ~900 (CSS) + ~660 (JS) + ~430 (tests) = **~2750 lines**

### Can present / demo:

```python
from src.evaluator import Evaluator
from src.lexer_parser import parse

ev = Evaluator()
ast = parse("nums = [1, 2, 3, 4, 5]\ntotal = 0\nfor x in nums:\n    total = total + x\nprint(total)\n")
output = ev.execute(ast)
print(output)        # "15\n"
print(ev.variables)  # {'nums': [1, 2, 3, 4, 5], 'total': 15, 'x': 5}
```

```bash
# Also demo the Compiler Visualizer IDE
python web_app.py
# → Open http://localhost:5000
# → Click "Arrays" snippet → Run — show all 5 panels + AST tree
```

---

## 📊 Summary Table

| Member | Compiler File(s) | Supporting File(s) | Total Lines |
|---|---|---|---|
| **Member 1** | `grammar.py` | `README.md`, `team_task_distribution.md`, `demo.mpy` | ~800 |
| **Member 2** | `ast_nodes.py`, `lexer_parser.py` | `requirements.txt` | ~446 |
| **Member 3** | `semantic_analyzer.py`, `cli.py` | `__init__.py`, `__main__.py` | ~525 |
| **Member 4** | `evaluator.py` | `web_app.py`, `web/`, `tests/` | ~2750 |

---

## 🎯 Presentation Order

| # | Who | Duration | What they present |
|---|---|---|---|
| 1 | **Member 1** | 3 min | Language design: grammar rules for loops & arrays, operator precedence, EBNF notation |
| 2 | **Member 2** | 3 min | AST design: 24-node hierarchy, parser transformer, how source becomes a tree, `tokenize()` API |
| 3 | **Member 3** | 4 min | Type system: symbol table with 6 types (int/float/char/bool/array/any), type inference, loop/array validation, CLI demo |
| 4 | **Member 4** | 5 min | Execution: Visitor Pattern, loop/array evaluation, enriched API, 3-column Compiler Visualizer IDE demo |
| 5 | **All** | 5 min | End-to-end live demo: enter code → see tokens → AST → types → validation → output. Q&A |

> [!TIP]
> **Suggested talking point:** *"Each of us built a separate module, but they all communicate through the AST — Member 2's parser produces it, Member 3's analyzer validates it, and Member 4's evaluator executes it. Member 1's grammar defines what's legal in the first place. The Compiler Visualizer IDE lets you see all five stages working in real time on the same screen."*

---

## ✅ Pre-Presentation Checklist

- [x] **All**: All language features implemented (loops, arrays, all operators)
- [x] **All**: All semantic analyzer type checks complete
- [x] **All**: All evaluator execution logic complete
- [ ] **Member 4**: Update test suite for new features (loops, arrays)
- [ ] **All**: Run `pytest tests/ -v` → **all passed, 0 failed**
- [ ] **All**: Each person can explain their files line-by-line if asked
- [ ] **All**: Each person can trace `print(1 + 2)` through their module
- [ ] **Member 3**: Demo the CLI REPL live
- [ ] **Member 4**: Demo the Compiler Visualizer IDE live
- [ ] **All**: Prepare for Q&A on array types, loop semantics, AST tree visualisation
