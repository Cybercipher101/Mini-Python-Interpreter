"""
cli.py — Command-Line Interface for the Mini-Python Interpreter
================================================================

This module provides two modes of operation:

  1. **File mode**: ``python -m src.cli <filename.mpy>``
     Reads the source file, parses, analyzes, evaluates, and prints output.

  2. **REPL mode**: ``python -m src.cli``
     An interactive Read-Eval-Print Loop where users type one statement
     at a time.

Error Handling Strategy
-----------------------
Each pipeline stage has its own exception type:

  • ``lark.exceptions.UnexpectedInput`` — syntax errors (frontend)
  • ``SemanticError``                   — type/scope errors (middleware)
  • ``EvalError``                       — runtime errors (backend)

The CLI catches all three and presents user-friendly messages colour-coded
by stage.
"""

from __future__ import annotations

import sys
from pathlib import Path

from lark.exceptions import UnexpectedInput

from src.evaluator import EvalError, Evaluator
from src.lexer_parser import parse
from src.semantic_analyzer import SemanticError, analyze


# ---------------------------------------------------------------------------
# ANSI colour helpers (degrade gracefully on Windows without colorama)
# ---------------------------------------------------------------------------

RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _colour(text: str, colour_code: str) -> str:
    """Wrap *text* in ANSI colour codes."""
    return f"{colour_code}{text}{RESET}"


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def run_source(
    source: str,
    evaluator: Evaluator | None = None,
    symbol_table: dict[str, str] | None = None,
) -> tuple[str, dict[str, str]]:
    """
    Execute the full interpreter pipeline on *source* and return output.

    Pipeline stages:
      1. Parse  (source → AST)
      2. Analyze (AST → symbol table, or raise SemanticError)
      3. Evaluate (AST → output string)

    Parameters
    ----------
    source : str
        Mini-Python source code.
    evaluator : Evaluator, optional
        An existing evaluator instance (for REPL state persistence).
        If ``None``, a fresh evaluator is created.
    symbol_table : dict[str, str], optional
        An existing symbol table (for REPL state persistence).
        If ``None``, a fresh symbol table is created.

    Returns
    -------
    tuple[str, dict[str, str]]
        A 2-tuple of (captured_output, updated_symbol_table).
    """
    ast = parse(source)
    symbol_table = analyze(ast, symbol_table=symbol_table)
    if evaluator is None:
        evaluator = Evaluator()
    output = evaluator.execute(ast)
    return output, symbol_table


# ---------------------------------------------------------------------------
# File mode
# ---------------------------------------------------------------------------

def run_file(filepath: str) -> None:
    """Read a ``.mpy`` file and execute it through the interpreter pipeline."""
    path = Path(filepath)

    if not path.exists():
        print(_colour(f"Error: File '{filepath}' not found.", RED))
        sys.exit(1)

    source = path.read_text(encoding="utf-8")

    try:
        output, _ = run_source(source)
        if output:
            print(output, end="")
    except UnexpectedInput as e:
        print(_colour("[Syntax Error]", RED))
        print(_colour(str(e), YELLOW))
        sys.exit(1)
    except SemanticError as e:
        print(_colour("[Semantic Error]", RED))
        print(_colour(str(e), YELLOW))
        sys.exit(1)
    except EvalError as e:
        print(_colour("[Runtime Error]", RED))
        print(_colour(str(e), YELLOW))
        sys.exit(1)


# ---------------------------------------------------------------------------
# REPL mode
# ---------------------------------------------------------------------------

def repl() -> None:
    """Launch an interactive Read-Eval-Print Loop."""
    print(_colour("Mini-Python Interpreter v1.0", BOLD + CYAN))
    print(_colour("Type 'exit' or 'quit' to leave.  Ctrl+C to cancel.\n", CYAN))

    evaluator = Evaluator()
    symbol_table: dict[str, str] = {}

    while True:
        try:
            line = input(_colour(">>> ", GREEN))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        # For if/elif/else blocks, accumulate lines until an empty line.
        if line.startswith("if "):
            lines = [line]
            while True:
                try:
                    continuation = input(_colour("... ", GREEN))
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    return
                if continuation.strip() == "":
                    break
                lines.append(continuation)
            source = "\n".join(lines)
        else:
            source = line

        try:
            output, symbol_table = run_source(
                source, evaluator=evaluator, symbol_table=symbol_table
            )
            if output:
                print(output, end="")
        except UnexpectedInput as e:
            print(_colour("[Syntax Error]", RED))
            print(_colour(str(e), YELLOW))
        except SemanticError as e:
            print(_colour("[Semantic Error]", RED))
            print(_colour(str(e), YELLOW))
        except EvalError as e:
            print(_colour("[Runtime Error]", RED))
            print(_colour(str(e), YELLOW))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point: file mode if argv[1] given, else REPL."""
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()


if __name__ == "__main__":
    main()
