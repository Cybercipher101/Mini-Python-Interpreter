# Mini-Python Interpreter

A modular, educational mini-Python interpreter built in Python 3.10+ using [Lark](https://lark-parser.readthedocs.io/) for grammar specification and parser generation. Includes a **Compiler Pipeline Visualizer IDE** — a 3-column browser-based development environment that shows every stage of the compilation process in real time.

## Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Supported Features](#supported-features)
- [Compiler Visualizer IDE](#compiler-visualizer-ide)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
  - [Web IDE (Recommended)](#web-ide-recommended)
  - [CLI — Run a File](#cli--run-a-file)
  - [CLI — Interactive REPL](#cli--interactive-repl)
- [Running Tests](#running-tests)
- [Debugging Guide](#debugging-guide)

---

## Quick Start

Get up and running in **3 commands**:

```bash
cd "Mini Python Interpreter"
pip install -r requirements.txt
python web_app.py
```

Then open **http://localhost:5000** in your browser. That's it — write and run mini-Python code instantly.

---

## Project Overview

This interpreter implements a **subset of Python** that supports:

- Integer, float, character, and boolean literals
- Arithmetic expressions with correct operator precedence
- Variable assignment (single global scope)
- Conditional statements (`if` / `elif` / `else`)
- Comparison and boolean operators (`==`, `!=`, `<`, `>`, `<=`, `>=`, `and`, `or`, `not`)
- Loop constructs (`while`, `for-in`, `do-while`)
- Array literals, indexing, and index assignment
- Built-in `range()` and `len()` functions
- A `print()` statement for output

It is designed as an **academic project** to teach compiler/interpreter design. The codebase is structured into three pipeline stages (Frontend, Middleware, Backend), each responsible for a distinct phase of the compilation process.

## Architecture

The interpreter follows a classic **five-stage compiler pipeline**, fully visualised in the IDE:

```
Source Code
    │
    ▼
┌──────────────────────────────┐
│  1. LEXER                    │  Tokenises source into lexemes
│     (Lark + grammar.py)      │  Output: Token stream
└──────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│  2. SYNTAX ANALYSER (Parser) │  src/grammar.py + src/lexer_parser.py
│     Lark LALR parser builds  │  Output: Abstract Syntax Tree (AST)
│     typed AST from tokens    │
└──────────────────────────────┘
    │  AST (ast_nodes.py)
    ▼
┌──────────────────────────────┐
│  3. SEMANTIC ANALYSER        │  src/semantic_analyzer.py
│     Symbol table, type       │  Output: Validated AST + symbol table
│     inference, scope checks  │
└──────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│  4. VALIDATOR                │  web_app.py (token stream checks)
│     Delimiter balance,       │  Output: Validation report
│     literal integrity,       │
│     structural checks        │
└──────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│  5. EXECUTOR (Evaluator)     │  src/evaluator.py
│     Visitor-pattern walk     │  Output: Program output + variables
│     Executes statements      │
└──────────────────────────────┘
    │
    ▼
  Output + Variable Store
```

Two interfaces connect users to the pipeline:

```
            ┌───────────────────────────────────────┐
            │  Compiler Visualizer IDE (web_app.py) │  ← 3-column browser IDE
            │  http://localhost:5000                 │     shows all 5 stages + AST
            └──────────┬────────────────────────────┘
                       │
  Source Code ─────────┼──────► Lex → Parse → Analyze → Validate → Execute
                       │
            ┌──────────┴────────────────────────────┐
            │  CLI (src/cli.py)                     │  ← Terminal-based (file + REPL)
            │  python -m src                        │
            └───────────────────────────────────────┘
```

### File Structure

```
Mini Python Interpreter/
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── team_task_distribution.md  # Team member file ownership
├── web_app.py                 # 🌐 Web IDE server (Flask) + enriched API
│
├── web/                       # 🌐 Compiler Visualizer IDE frontend
│   ├── templates/
│   │   └── index.html         #    3-column IDE layout
│   └── static/
│       ├── style.css          #    Dark theme, stage panels, AST tree styles
│       └── app.js             #    Pipeline orchestration & AST tree renderer
│
├── examples/
│   └── demo.mpy               # Example program
│
├── src/                       # ⚙️ Interpreter core
│   ├── __init__.py            #    Package init
│   ├── __main__.py            #    Entry: python -m src
│   ├── grammar.py             #    Lark EBNF grammar (with loops & arrays)
│   ├── ast_nodes.py           #    AST node dataclasses (24 nodes)
│   ├── lexer_parser.py        #    Frontend: parsing + AST construction + tokenize()
│   ├── semantic_analyzer.py   #    Middleware: type checking (int/float/char/bool/array/any)
│   ├── evaluator.py           #    Backend: execution engine (with loops & arrays)
│   └── cli.py                 #    CLI interface (file + REPL)
│
└── tests/                     # 🧪 Test suite
    ├── __init__.py
    └── test_interpreter.py    #    85 Pytest tests across 5 classes
```

## Supported Features

| Feature | Syntax Example | Status |
|---|---|---|
| Integers | `42`, `-7` | ✅ Complete |
| Floats | `3.14`, `-0.5` | ✅ Complete |
| Characters | `'a'`, `'Z'` | ✅ Complete |
| Booleans | `True`, `False` | ✅ Complete |
| Addition | `x + y` | ✅ Complete |
| Subtraction | `x - y` | ✅ Complete |
| Multiplication | `x * y` | ✅ Complete |
| True Division | `x / y` | ✅ Complete |
| Floor Division | `x // y` | ✅ Complete |
| Modulo | `x % y` | ✅ Complete |
| Exponentiation | `x ** y` | ✅ Complete |
| Unary +/- | `-x`, `+y` | ✅ Complete |
| Comparisons == != | `x == y` | ✅ Complete |
| Comparisons < > <= >= | `x < y` | ✅ Complete |
| Boolean and/or | `x and y` | ✅ Complete |
| Boolean not | `not x` | ✅ Complete |
| Variable Assignment | `x = 42` | ✅ Complete |
| `if` statement | `if x == 1:` | ✅ Complete |
| `elif` clause | `elif x == 2:` | ✅ Complete |
| `else` clause | `else:` | ✅ Complete |
| `while` loop | `while x > 0:` | ✅ Complete |
| `for-in` loop | `for i in range(5):` | ✅ Complete |
| `do-while` loop | `do: ... while cond` | ✅ Complete |
| Array literals | `[1, 2, 3]` | ✅ Complete |
| Index access | `arr[0]` | ✅ Complete |
| Index assignment | `arr[2] = 99` | ✅ Complete |
| `range()` | `range(5)`, `range(1,10,2)` | ✅ Complete |
| `len()` | `len(arr)` | ✅ Complete |
| Print | `print(expr)` | ✅ Complete |

---

## Compiler Visualizer IDE

The Web IDE is a **3-column compiler pipeline visualizer** that shows every stage of compilation in real time.

### Layout

| Column | Content |
|---|---|
| **Left** — Code Editor | Syntax-highlighted textarea with line numbers, Tab support, and example snippet buttons |
| **Center** — Pipeline Panels | 5 scrollable panels showing the output of each compiler stage |
| **Right** — AST Tree | Interactive, collapsible tree with branch lines from root to terminals |

### Pipeline Panels

Each panel shows real-time output from a compiler stage:

| # | Panel | What It Shows |
|---|---|---|
| 01 | **Lexer** | Token table — Type (colour-coded badge), Lexeme, Line Number |
| 02 | **Syntax Analyser** | Parse success / syntax error messages with line numbers |
| 03 | **Semantic Analyser** | Symbol table (variable → type mapping), semantic errors |
| 04 | **Validator** | Delimiter balance, literal integrity, line structure checks |
| 05 | **Executor** | Program output lines with execution time |

### AST Tree Panel

- **Branching tree** with CSS-drawn connector lines (`├──` / `└──` style) from root to every leaf
- **Edge labels** on branches (`left:`, `right:`, `condition:`, `body[0]:`)
- **Colour-coded nodes** by category: statements (blue), loops (purple), operators (pink), literals (green pill), variables (cyan pill), arrays (orange), builtins (yellow)
- **Collapsible** — click any parent node to expand/collapse its subtree
- **Expand All / Collapse All** buttons in the panel header

### Example Snippets

Click any snippet button to load pre-written code:

| Button | What It Demonstrates |
|---|---|
| Arithmetic | All operators (`+`, `-`, `*`, `/`, `//`, `%`, `**`) |
| If/Elif/Else | Conditional branching |
| While | `while` loop with accumulator |
| For | `for-in` loop over an array |
| Do-While | `do-while` loop |
| Arrays | Array literals, `len()`, indexing, `range()` |
| Operators | Floor div, modulo, exponentiation, boolean logic |

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Run / Compile |
| `Tab` | Insert 4 spaces |

---

## Setup & Installation

### Prerequisites

- **Python 3.10 or higher** (required for `match`/`case` syntax and `X | Y` type unions)
- **pip** (Python package manager)
- A modern **web browser** (for the Web IDE)

### Step-by-Step Setup

1. **Navigate** to the project directory:
   ```bash
   cd "Mini Python Interpreter"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python -c "import lark; print('Lark version:', lark.__version__)"
   python -c "import pytest; print('Pytest version:', pytest.__version__)"
   python -c "import flask; print('Flask version:', flask.__version__)"
   ```

---

## Usage

### Web IDE (Recommended)

The **easiest way** to use the interpreter — a full compiler visualizer IDE.

**Start the server:**

```bash
python web_app.py
```

**Open your browser** and go to:

```
http://localhost:5000
```

**What you get:**

- 📝 **Code editor** with line numbers, Tab indentation, and snippet buttons
- ▶️ **Run / Compile button** (or press `Ctrl+Enter`) to execute code and populate all panels
- 📊 **5 simultaneous pipeline panels** — Lexer, Syntax, Semantic, Validator, Executor
- 🌳 **Interactive AST tree** — collapsible branching tree from root to every terminal
- 🎯 **7 example snippets** — Arithmetic, If/Elif/Else, While, For, Do-While, Arrays, Operators
- 🎨 **Colour-coded errors** — errors indicate which pipeline stage caused the problem

**Example workflow:**

1. Click the **"For"** snippet button to load a for-loop example
2. Click **▶ Run / Compile** (or press `Ctrl+Enter`)
3. See the **Lexer** panel populate with the token stream
4. See the **Syntax Analyser** confirm grammar satisfaction
5. See the **Semantic Analyser** show the symbol table with variable types
6. See the **Validator** confirm delimiter balance and literal integrity
7. See the **Executor** display the output (`15`)
8. Browse the **AST Tree** on the right — expand/collapse nodes to explore the tree structure

---

### CLI — Run a File

Create a `.mpy` file with mini-Python code, then execute it:

```bash
python -m src examples/demo.mpy
```

Example output:

```
212.0
10
4
21
2.3333333333333335
True
A
True
```

---

### CLI — Interactive REPL

Launch the Read-Eval-Print Loop for line-by-line execution:

```bash
python -m src
```

Example session:

```
Mini-Python Interpreter v1.0
Type 'exit' or 'quit' to leave.  Ctrl+C to cancel.

>>> x = 42
>>> print(x + 8)
50
>>> print(x == 42)
True
>>> exit
Goodbye!
```

> **Note:** For `if` blocks in the REPL, type the full block and press Enter on an empty line to execute:
>
> ```
> >>> if True:
> ...     print(1)
> ...
> 1
> ```

---

## All Three Ways to Run — Summary

| Method | Command | Best for |
|---|---|---|
| 🌐 **Web IDE** | `python web_app.py` → open browser | Visualising the compiler pipeline, debugging, presentations |
| 📄 **File mode** | `python -m src myfile.mpy` | Running complete programs |
| 💻 **REPL** | `python -m src` | Interactive line-by-line experimentation |

---

## Running Tests

### Run all tests

```bash
pytest tests/ -v
```

### Run with short tracebacks

```bash
pytest tests/ -v --tb=short
```

### Run a specific test class

```bash
pytest tests/test_interpreter.py::TestEvaluator -v
```

### Run tests matching a keyword

```bash
pytest tests/ -v -k "floor_division"
```

### Run with coverage report

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Understanding test results

- **PASSED** — The feature is implemented and working.
- **XFAIL** — The test is *expected to fail* because the corresponding `TODO` is not yet implemented. Once you implement it, the test will change to **XPASS** (unexpectedly passed), which Pytest treats as a warning.
- **FAILED** — Something is broken. Use the debugging guide below to diagnose.

> **Tip:** After implementing a TODO, remove the `@pytest.mark.xfail` decorator from the corresponding test(s) so that failures are reported properly.

## Debugging Guide

### General Strategy

When something fails, **isolate which layer** is causing the problem:

```
Source → [LEXER/PARSER] → AST → [SEMANTIC ANALYZER] → AST → [EVALUATOR] → Output
         Syntax errors      Type/scope errors           Runtime errors
```

> **Tip:** The **Web IDE** shows which stage caused the error right in the pipeline panels. Each panel has a pass/fail badge. Check the first panel with a ✗ badge to find the failing stage.

### 1. Debugging Syntax Errors (Frontend)

**Symptoms:** `UnexpectedInput`, `UnexpectedToken`, `UnexpectedCharacters`

**In the Web IDE:** The **Syntax Analyser** panel (02) shows a ✗ badge with the error message.

**Steps:**

1. **Check the grammar** (`src/grammar.py`). Is your syntax rule defined?
2. **Print the raw parse tree** before AST transformation:
   ```python
   from src.grammar import MINI_PYTHON_GRAMMAR
   from lark import Lark
   from src.lexer_parser import MiniPythonIndenter

   parser = Lark(MINI_PYTHON_GRAMMAR, parser="lalr",
                 postlex=MiniPythonIndenter(), start="program")
   tree = parser.parse("your code here\n")
   print(tree.pretty())  # Visualise the raw parse tree
   ```
3. **Check indentation**. Lark's `Indenter` is sensitive to mixing tabs/spaces.
4. **Verify terminal patterns**. If a token isn't matching, check `CHAR`, `INT`, `FLOAT` regex patterns.

### 2. Debugging Type Errors (Middleware)

**Symptoms:** `SemanticError` with messages like "Type mismatch" or "Undefined variable"

**In the Web IDE:** The **Semantic Analyser** panel (03) shows a ✗ badge and the symbol table shows inferred types up to the point of failure.

**Steps:**

1. **Inspect the symbol table** after analysis:
   ```python
   from src.lexer_parser import parse
   from src.semantic_analyzer import SemanticAnalyzer

   ast = parse("x = 42\ny = x + 1.0\n")
   analyzer = SemanticAnalyzer()
   analyzer.analyze(ast)
   print(analyzer.symbol_table)  # {'x': 'int', 'y': 'float'}
   ```
2. **Trace type inference**. Add `print()` calls inside `_infer_type` to see what type each sub-expression resolves to.
3. **Check promotion rules** in `_check_binary_op`. Missing promotion cases fall through to the generic error.

### 3. Debugging Runtime Errors (Backend)

**Symptoms:** `EvalError`, wrong output, or Python exceptions

**In the Web IDE:** The **Executor** panel (05) shows a ✗ badge with the error message. Previous panels will all show ✓.

**Steps:**

1. **Parse and inspect the AST** first to confirm it's correct:
   ```python
   from src.lexer_parser import parse
   ast = parse("print(1 + 2)\n")
   print(ast)  # Verify the AST structure
   ```
2. **Step through the evaluator** manually. Add `print()` inside `_eval` to trace the dispatch:
   ```python
   def _eval(self, node):
       print(f"Evaluating: {type(node).__name__} → {node}")
       # ... existing dispatch code ...
   ```
3. **Inspect variable state** (also visible in the Web IDE's **Semantic Analyser** panel):
   ```python
   from src.evaluator import Evaluator
   from src.lexer_parser import parse

   ev = Evaluator()
   ast = parse("x = 10\ny = x + 5\n")
   ev.execute(ast)
   print(ev.variables)  # {'x': 10, 'y': 15}
   ```

### 4. Common Pitfalls

| Problem | Likely cause | Fix |
|---|---|---|
| `UnexpectedToken: Expected _NL` | Missing newline at end of source | `parse()` adds `\n` automatically |
| `match/case` syntax error | Python < 3.10 | Upgrade to Python 3.10+ |
| XFAIL test suddenly XPASS | You implemented a TODO! | Remove `@pytest.mark.xfail` |
| `isinstance` checks fail | Wrong import path | Always import from `src.ast_nodes` |
| REPL doesn't accept `if` blocks | Didn't enter empty line | Press Enter on blank line to submit |
| Web IDE shows "Connection Error" | Server not running | Run `python web_app.py` first |
| `Index out of bounds` | Invalid array index | Check `len(arr)` before accessing |
| `While loop exceeded max iterations` | Infinite loop | Add a termination condition |

---

## License

This project is for **academic/educational use only**.
