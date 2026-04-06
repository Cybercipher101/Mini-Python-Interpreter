"""
web_app.py — Flask Web Server for the Mini-Python Interpreter
===============================================================

Provides a browser-based IDE for writing and executing mini-Python code.

Endpoints:
    GET  /          — Serves the web IDE
    POST /api/run   — Executes mini-Python code and returns full pipeline data

Usage:
    python web_app.py
    Then open http://localhost:5000 in your browser.
"""

from __future__ import annotations

import traceback
from flask import Flask, render_template, request, jsonify

from src.lexer_parser import parse, tokenize
from src.semantic_analyzer import SemanticError, SemanticAnalyzer
from src.evaluator import EvalError, evaluate

app = Flask(
    __name__,
    template_folder="web/templates",
    static_folder="web/static",
)


@app.route("/")
def index():
    """Serve the web IDE."""
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def run_code():
    """
    Execute mini-Python code and return full pipeline JSON response.

    Request JSON:
        { "code": "<source code string>" }

    Response JSON:
        {
            "success": true/false,
            "tokens": [{"type": "...", "lexeme": "...", "line": N}, ...],
            "ast": { ... structured AST ... },
            "ast_preview": "...",
            "syntax_errors": [],
            "semantic_errors": [],
            "semantic_info": { "symbol_table": {...} },
            "validation": { "checks": [...] },
            "output": "...",
            "variables": { ... },
            "error": null or { "type": "...", "message": "...", "stage": "..." }
        }
    """
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"success": False, "error": {
            "type": "Request Error",
            "message": "No code provided."
        }}), 400

    source = data["code"]

    # Empty source
    if not source.strip():
        return jsonify({
            "success": True,
            "tokens": [],
            "ast": None,
            "ast_preview": "Empty program",
            "syntax_errors": [],
            "semantic_errors": [],
            "semantic_info": {"symbol_table": {}},
            "validation": {"checks": []},
            "output": "",
            "error": None,
            "variables": {},
        })

    # ── Stage 0: Tokenize (always attempted) ──
    tokens = tokenize(source)

    # ── Validation checks on tokens ──
    validation_checks = _run_validation(source, tokens)

    # ── Stage 1: Parse ──
    try:
        ast = parse(source)
    except Exception as e:
        return jsonify({
            "success": False,
            "tokens": tokens,
            "ast": None,
            "ast_preview": None,
            "syntax_errors": [str(e)],
            "semantic_errors": [],
            "semantic_info": {"symbol_table": {}},
            "validation": {"checks": validation_checks},
            "output": "",
            "error": {
                "type": "Syntax Error",
                "stage": "Frontend (Lexer/Parser)",
                "message": str(e),
            },
            "variables": {},
        })

    # Generate AST data
    ast_preview = _ast_to_string(ast)
    ast_json = _ast_to_json(ast)

    # ── Stage 2: Semantic Analysis ──
    semantic_errors = []
    symbol_table = {}
    try:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        symbol_table = analyzer.symbol_table
    except SemanticError as e:
        semantic_errors = [str(e)]
        symbol_table = analyzer.symbol_table  # partial table still useful
        return jsonify({
            "success": False,
            "tokens": tokens,
            "ast": ast_json,
            "ast_preview": ast_preview,
            "syntax_errors": [],
            "semantic_errors": semantic_errors,
            "semantic_info": {"symbol_table": symbol_table},
            "validation": {"checks": validation_checks},
            "output": "",
            "error": {
                "type": "Semantic Error",
                "stage": "Middleware (Semantic Analyzer)",
                "message": str(e),
            },
            "variables": {},
        })

    # ── Stage 3: Evaluate ──
    try:
        output, variables = evaluate(ast)
    except (EvalError, Exception) as e:
        err_type = "Runtime Error" if isinstance(e, EvalError) else "Internal Error"
        return jsonify({
            "success": False,
            "tokens": tokens,
            "ast": ast_json,
            "ast_preview": ast_preview,
            "syntax_errors": [],
            "semantic_errors": [],
            "semantic_info": {"symbol_table": symbol_table},
            "validation": {"checks": validation_checks},
            "output": "",
            "error": {
                "type": err_type,
                "stage": "Backend (Evaluator)",
                "message": str(e),
            },
            "variables": {},
        })

    # Format variables for JSON
    formatted_vars = {}
    for name, val in variables.items():
        if isinstance(val, bool):
            formatted_vars[name] = {"value": str(val), "type": "bool"}
        elif isinstance(val, int):
            formatted_vars[name] = {"value": str(val), "type": "int"}
        elif isinstance(val, float):
            formatted_vars[name] = {"value": str(val), "type": "float"}
        elif isinstance(val, str):
            formatted_vars[name] = {"value": repr(val), "type": "char"}
        elif isinstance(val, list):
            formatted_vars[name] = {"value": _format_list(val), "type": "array"}

    return jsonify({
        "success": True,
        "tokens": tokens,
        "ast": ast_json,
        "ast_preview": ast_preview,
        "syntax_errors": [],
        "semantic_errors": [],
        "semantic_info": {"symbol_table": symbol_table},
        "validation": {"checks": validation_checks},
        "output": output,
        "error": None,
        "variables": formatted_vars,
    })


# ---------------------------------------------------------------------------
# AST serialization helpers
# ---------------------------------------------------------------------------

def _ast_to_string(node, indent=0) -> str:
    """Create a readable string representation of the AST."""
    prefix = "  " * indent
    name = type(node).__name__

    if hasattr(node, '__dataclass_fields__'):
        fields = []
        for field_name in node.__dataclass_fields__:
            val = getattr(node, field_name)
            if isinstance(val, tuple):
                items = [_ast_to_string(item, indent + 1) for item in val]
                if items:
                    fields.append(f"{prefix}  {field_name}:\n" + "\n".join(items))
                else:
                    fields.append(f"{prefix}  {field_name}: []")
            elif hasattr(val, '__dataclass_fields__'):
                fields.append(f"{prefix}  {field_name}:\n{_ast_to_string(val, indent + 2)}")
            else:
                fields.append(f"{prefix}  {field_name}: {repr(val)}")
        return f"{prefix}{name}\n" + "\n".join(fields)
    return f"{prefix}{repr(node)}"


def _ast_to_json(node) -> dict | str | int | float | bool | list | None:
    """Convert an AST node to a JSON-serializable dict."""
    if node is None:
        return None

    if isinstance(node, (int, float, str, bool)):
        return node

    if isinstance(node, tuple):
        return [_ast_to_json(item) for item in node]

    if isinstance(node, list):
        return [_ast_to_json(item) for item in node]

    if hasattr(node, '__dataclass_fields__'):
        result = {"_type": type(node).__name__}
        for field_name in node.__dataclass_fields__:
            val = getattr(node, field_name)
            result[field_name] = _ast_to_json(val)
        return result

    return str(node)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _run_validation(source: str, tokens: list[dict]) -> list[dict]:
    """Run basic validation checks on the source and token stream."""
    checks = []

    # 1. Delimiter balance
    delim_stack = []
    delim_pairs = {"(": ")", "[": "]", "{": "}"}
    delim_errors = []
    for tok in tokens:
        lexeme = tok.get("lexeme", "")
        if lexeme in delim_pairs:
            delim_stack.append((lexeme, tok.get("line", 0)))
        elif lexeme in delim_pairs.values():
            if delim_stack and delim_pairs.get(delim_stack[-1][0]) == lexeme:
                delim_stack.pop()
            else:
                delim_errors.append(f"Unmatched '{lexeme}' at line {tok.get('line', '?')}")
    for opener, line in delim_stack:
        delim_errors.append(f"Unmatched '{opener}' opened at line {line}")

    checks.append({
        "name": "Delimiter Balance",
        "status": "pass" if not delim_errors else "fail",
        "details": "All delimiters balanced" if not delim_errors else "; ".join(delim_errors),
    })

    # 2. Literal type validation
    literal_issues = []
    for tok in tokens:
        if tok["type"] == "INT":
            try:
                int(tok["lexeme"])
            except ValueError:
                literal_issues.append(f"Invalid integer '{tok['lexeme']}' at line {tok['line']}")
        elif tok["type"] == "FLOAT":
            try:
                float(tok["lexeme"])
            except ValueError:
                literal_issues.append(f"Invalid float '{tok['lexeme']}' at line {tok['line']}")

    checks.append({
        "name": "Literal Type Validation",
        "status": "pass" if not literal_issues else "fail",
        "details": "All literals are valid" if not literal_issues else "; ".join(literal_issues),
    })

    # 3. Line ordering / structure
    lines = source.split("\n")
    ordering_issues = []
    for i, line in enumerate(lines, 1):
        if line and not line.startswith(" ") and not line.startswith("\t"):
            continue
        stripped = line.lstrip()
        if stripped and line != stripped:
            indent = len(line) - len(stripped)
            if indent % 4 != 0 and indent % 2 != 0:
                ordering_issues.append(f"Irregular indentation at line {i} ({indent} spaces)")

    checks.append({
        "name": "Line Structure",
        "status": "pass" if not ordering_issues else "warn",
        "details": "Line structure is consistent" if not ordering_issues else "; ".join(ordering_issues),
    })

    return checks


def _format_list(lst: list) -> str:
    """Format a list value for JSON display."""
    parts = []
    for v in lst:
        if isinstance(v, bool):
            parts.append(str(v))
        elif isinstance(v, list):
            parts.append(_format_list(v))
        else:
            parts.append(repr(v) if isinstance(v, str) else str(v))
    return f"[{', '.join(parts)}]"


if __name__ == "__main__":
    print("\n  Mini-Python Interpreter — Web IDE")
    print("  Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
