"""
web_app.py — Flask Web Server for the Mini-Python Interpreter
===============================================================

Provides a browser-based IDE for writing and executing mini-Python code.

Endpoints:
    GET  /          — Serves the web IDE
    POST /api/run   — Executes mini-Python code and returns output/errors

Usage:
    python web_app.py
    Then open http://localhost:5000 in your browser.
"""

from __future__ import annotations

import traceback
from flask import Flask, render_template, request, jsonify

from src.lexer_parser import parse
from src.semantic_analyzer import SemanticError, analyze
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
    Execute mini-Python code and return JSON response.

    Request JSON:
        { "code": "<source code string>" }

    Response JSON:
        {
            "success": true/false,
            "output": "...",
            "error": null or { "type": "...", "message": "..." },
            "variables": { "name": value, ... },
            "ast_preview": "..."
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
            "output": "",
            "error": None,
            "variables": {},
            "ast_preview": "Empty program",
        })

    # Stage 1: Parse
    try:
        ast = parse(source)
    except Exception as e:
        return jsonify({
            "success": False,
            "output": "",
            "error": {
                "type": "Syntax Error",
                "stage": "Frontend (Lexer/Parser)",
                "message": str(e),
            },
            "variables": {},
            "ast_preview": None,
        })

    # Generate AST preview string
    ast_preview = _ast_to_string(ast)

    # Stage 2: Semantic Analysis
    try:
        symbol_table = analyze(ast)
    except SemanticError as e:
        return jsonify({
            "success": False,
            "output": "",
            "error": {
                "type": "Semantic Error",
                "stage": "Middleware (Semantic Analyzer)",
                "message": str(e),
            },
            "variables": {},
            "ast_preview": ast_preview,
        })

    # Stage 3: Evaluate
    try:
        output, variables = evaluate(ast)
    except EvalError as e:
        return jsonify({
            "success": False,
            "output": "",
            "error": {
                "type": "Runtime Error",
                "stage": "Backend (Evaluator)",
                "message": str(e),
            },
            "variables": {},
            "ast_preview": ast_preview,
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "output": "",
            "error": {
                "type": "Internal Error",
                "stage": "Backend (Evaluator)",
                "message": str(e),
            },
            "variables": {},
            "ast_preview": ast_preview,
        })

    # Format variables for JSON (convert single-char strings etc.)
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

    return jsonify({
        "success": True,
        "output": output,
        "error": None,
        "variables": formatted_vars,
        "ast_preview": ast_preview,
    })


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


if __name__ == "__main__":
    print("\n  Mini-Python Interpreter — Web IDE")
    print("  Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
