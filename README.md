# Mini-Python Interpreter

A modular, educational mini-Python interpreter built in Python 3.10+ using [Lark](https://lark-parser.readthedocs.io/) for grammar specification and parser generation. Includes a **Web-based IDE** for easy access — no terminal required.

## Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Supported Features](#supported-features)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
  - [Web IDE (Recommended)](#web-ide-recommended)
  - [CLI — Run a File](#cli--run-a-file)
  - [CLI — Interactive REPL](#cli--interactive-repl)
- [Running Tests](#running-tests)
- [TODO Exercises](#todo-exercises)
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

- Integer, float,     character, and boolean literals
- Arithmetic expressions with correct operator precedence
- Variable assignment (single global scope)
- Basic conditional statements (`if` / `elif` / `else`)
- Comparison and boolean operators
- A `print()` statement for output

It is designed as an **academic project** to teach compiler/interpreter design. The codebase is approximately **70–80% complete**; students are expected to implement the remaining `TODO` blocks, run the test suite to validate their work, and debug across the modular layers.

## Architecture

The interpreter follows a classic **three-stage pipeline**:

```
Source Code
    │
    ▼
┌──────────────────────────────┐
│  1. FRONTEND (Lexer/Parser)  │  src/grammar.py + src/lexer_parser.py
│  Lark tokenises and parses   │
│  source → AST                │
└──────────────────────────────┘
    │  AST (ast_nodes.py)
    ▼
┌──────────────────────────────┐
│  2. MIDDLEWARE (Sem. Analyzer)│  src/semantic_analyzer.py
│  Symbol table + type checker │
│  Catches type/scope errors   │
└──────────────────────────────┘
    │  Validated AST
    ▼
┌──────────────────────────────┐
│  3. BACKEND (Evaluator)      │  src/evaluator.py
│  Visitor-pattern tree walk   │
│  Executes statements         │
└──────────────────────────────┘
    │
    ▼
  Output
```

Two interfaces connect users to the pipeline:

```
            ┌──────────────────────────┐
            │   Web IDE (web_app.py)   │  ← Browser-based, easiest to use
            │   http://localhost:5000  │
            └─────────┬────────────────┘
                      │
  Source Code ────────┼──────► Parse → Analyze → Evaluate → Output
                      │
            ┌─────────┴────────────────┐
            │   CLI (src/cli.py)       │  ← Terminal-based (file + REPL)
            │   python -m src          │
            └──────────────────────────┘
```

### File Structure

```
Mini Python Interpreter/
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── web_app.py                 # 🌐 Web IDE server (Flask)
│
├── web/                       # 🌐 Web IDE frontend
│   ├── templates/
│   │   └── index.html         #    IDE layout & structure
│   └── static/
│       ├── style.css          #    Dark theme design system
│       └── app.js             #    Editor logic & API calls
│
├── examples/
│   └── demo.mpy               # Example program
│
├── src/                       # ⚙️ Interpreter core
│   ├── __init__.py            #    Package init
│   ├── __main__.py            #    Entry: python -m src
│   ├── grammar.py             #    Lark EBNF grammar
│   ├── ast_nodes.py           #    AST node dataclasses
│   ├── lexer_parser.py        #    Frontend: parsing + AST construction
│   ├── semantic_analyzer.py   #    Middleware: type checking
│   ├── evaluator.py           #    Backend: execution engine
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
| Floor Division | `x // y` | 🔧 TODO |
| Modulo | `x % y` | 🔧 TODO |
| Exponentiation | `x ** y` | 🔧 TODO |
| Unary +/- | `-x`, `+y` | ✅ Complete |
| Comparisons == != | `x == y` | ✅ Complete |
| Comparisons < > <= >= | `x < y` | 🔧 TODO |
| Boolean and/or | `x and y` | 🔧 TODO |
| Boolean not | `not x` | ✅ Complete |
| Variable Assignment | `x = 42` | ✅ Complete |
| `if` statement | `if x == 1:` | ✅ Complete |
| `elif` clause | `elif x == 2:` | 🔧 TODO |
| `else` clause | `else:` | 🔧 TODO |
| Print | `print(expr)` | ✅ Complete |

> **🔧 TODO** items are left as student exercises with detailed instructions in the source code.

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

The **easiest way** to use the interpreter — no terminal knowledge needed.

**Start the server:**

```bash
python web_app.py
```

**Open your browser** and go to:

```
http://localhost:5000
```

**What you get:**

- 📝 **Code editor** with line numbers and Tab indentation support
- ▶️ **Run button** (or press `Ctrl+Enter`) to execute code instantly
- 📊 **Three output tabs:**
  - **Output** — printed results with success/error indicators
  - **Variables** — table showing all variable names, values, and types
  - **AST** — the Abstract Syntax Tree visualization
- 🎯 **Example snippets** — click "Arithmetic", "Variables", "Conditionals", or "Types" to load pre-written examples
- 🎨 **Color-coded errors** — errors indicate which pipeline stage (Syntax / Semantic / Runtime) caused the problem

**Example workflow:**

1. Click the **"Variables"** snippet button to load sample code
2. Click **▶ Run** (or press `Ctrl+Enter`)
3. See the output in the **Output** tab
4. Switch to the **Variables** tab to inspect variable types
5. Switch to the **AST** tab to see the parse tree structure

> **Tip:** The Web IDE is stateless — each run executes the full program from scratch. For stateful, line-by-line interaction, use the CLI REPL instead.

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
| 🌐 **Web IDE** | `python web_app.py` → open browser | Beginners, visual learners, quick testing |
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

## TODO Exercises

Search the codebase for `TODO` to find all exercises. Here is a summary:

### Evaluator (`src/evaluator.py`)

| # | Method | Exercise |
|---|---|---|
| 1 | `_eval_binary_op` | Implement floor division (`//`) with zero guard |
| 2 | `_eval_binary_op` | Implement modulo (`%`) with zero guard |
| 3 | `_eval_binary_op` | Implement exponentiation (`**`) |
| 4 | `_eval_comparison` | Implement `<`, `>`, `<=`, `>=` |
| 5 | `_eval_boolean_op` | Implement short-circuit `and` / `or` |
| 6 | `_exec_if` | Implement `elif` clause evaluation |
| 7 | `_exec_if` | Implement `else` clause fallback |

### Semantic Analyzer (`src/semantic_analyzer.py`)

| # | Method | Exercise |
|---|---|---|
| 1 | `_check_binary_op` | Modulo with float promotion |
| 2 | `_check_binary_op` | Floor division with float promotion |
| 3 | `_check_binary_op` | Power with mixed types |
| 4 | `_check_binary_op` | Error on char operands |
| 5 | `_check_binary_op` | Error on bool operands |
| 6 | `_check_comparison` | Bool-to-bool equality comparison |
| 7 | `_check_comparison` | Explicit cross-type error message |

## Debugging Guide

### General Strategy

When something fails, **isolate which layer** is causing the problem:

```
Source → [LEXER/PARSER] → AST → [SEMANTIC ANALYZER] → AST → [EVALUATOR] → Output
         Syntax errors      Type/scope errors           Runtime errors
```

> **Tip:** The **Web IDE** shows which stage caused the error right in the output panel. Look for "Stage: Frontend", "Stage: Middleware", or "Stage: Backend" in the error message.

### 1. Debugging Syntax Errors (Frontend)

**Symptoms:** `UnexpectedInput`, `UnexpectedToken`, `UnexpectedCharacters`

**In the Web IDE:** You'll see a red error banner with **"Stage: Frontend (Lexer/Parser)"**.

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

**In the Web IDE:** You'll see **"Stage: Middleware (Semantic Analyzer)"**.

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

**In the Web IDE:** You'll see **"Stage: Backend (Evaluator)"**.

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
3. **Inspect variable state** (also visible in the Web IDE's **Variables** tab):
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

---

## License

This project is for **academic/educational use only**.
