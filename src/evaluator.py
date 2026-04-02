"""
evaluator.py — Backend: AST Evaluator (Visitor Pattern)
========================================================

The evaluator is the **execution engine** of the interpreter.  It performs
a depth-first traversal of the AST, computing values and executing
statements.

Architecture
------------
The evaluator follows the **Visitor Pattern**: each AST node type has a
corresponding ``_eval_*`` method.  The central ``_eval`` dispatcher
matches the node's class and delegates to the right visitor method.

Runtime State
-------------
* ``self.variables`` — a single flat ``dict[str, object]`` acting as the
  global variable store.

Error Handling
--------------
* ``EvalError`` is raised for runtime errors (division by zero, undefined
  variable access that slipped past semantic analysis, etc.).

TODO Blocks for Students
-------------------------
Several visitor methods are left partially or fully unimplemented.
Search for ``TODO`` to find them.  The architectural wiring (dispatcher,
print, assignment, if-statement skeleton) is complete.
"""

from __future__ import annotations

import io
from typing import Any

from src.ast_nodes import (
    ASTNode,
    Assignment,
    BinaryOp,
    BooleanOp,
    BoolLiteral,
    CharLiteral,
    Comparison,
    ElifClause,
    ElseClause,
    FloatLiteral,
    IfStatement,
    IntLiteral,
    NotOp,
    PrintStatement,
    Program,
    UnaryOp,
    Variable,
)


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class EvalError(Exception):
    """Raised when a runtime evaluation error occurs."""
    pass


# ---------------------------------------------------------------------------
# Value type (union of all possible runtime values)
# ---------------------------------------------------------------------------

Value = int | float | str | bool  # str is always a single character


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class Evaluator:
    """
    Executes a mini-Python AST.

    Attributes
    ----------
    variables : dict[str, Value]
        Global variable store.
    output_buffer : io.StringIO
        Captures ``print`` output for testing.  The CLI drains this
        after each execution.
    """

    def __init__(self) -> None:
        self.variables: dict[str, Value] = {}
        self.output_buffer: io.StringIO = io.StringIO()

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def execute(self, program: Program) -> str:
        """
        Execute a full program and return its captured output.

        Parameters
        ----------
        program : Program
            The root AST node.

        Returns
        -------
        str
            All text written by ``print`` statements.
        """
        for stmt in program.statements:
            self._exec_statement(stmt)
        return self.output_buffer.getvalue()

    def get_variable(self, name: str) -> Value:
        """Retrieve a variable's current value (useful for testing)."""
        if name not in self.variables:
            raise EvalError(f"Undefined variable: '{name}'")
        return self.variables[name]

    # -----------------------------------------------------------------------
    # Statement execution
    # -----------------------------------------------------------------------

    def _exec_statement(self, node: ASTNode) -> None:
        """Dispatch a statement node to its handler."""
        if isinstance(node, Assignment):
            self._exec_assignment(node)
        elif isinstance(node, PrintStatement):
            self._exec_print(node)
        elif isinstance(node, IfStatement):
            self._exec_if(node)
        else:
            raise EvalError(f"Unknown statement type: {type(node).__name__}")

    def _exec_assignment(self, node: Assignment) -> None:
        """Evaluate the RHS and bind the result to the variable name."""
        value = self._eval(node.value)
        self.variables[node.name] = value

    def _exec_print(self, node: PrintStatement) -> None:
        """Evaluate the expression and write the result to the output buffer."""
        value = self._eval(node.expression)
        # Format characters with surrounding quotes to distinguish them
        # from single-char strings in the output.
        if isinstance(value, str) and len(value) == 1:
            self.output_buffer.write(f"{value}\n")
        elif isinstance(value, bool):
            # Python's bool is a subclass of int; print True/False explicitly.
            self.output_buffer.write(f"{value}\n")
        else:
            self.output_buffer.write(f"{value}\n")

    def _exec_if(self, node: IfStatement) -> None:
        """
        Execute an if / elif / else compound statement.

        TODO (Student Exercise):
        ────────────────────────
        The ``if`` branch is implemented below.  You must implement:

          1. **elif evaluation**: Iterate over ``node.elif_clauses``.
             For each ``ElifClause``, evaluate its condition.  If truthy,
             execute its body and return immediately (short-circuit).

          2. **else fallback**: If no ``if`` or ``elif`` branch was taken
             and ``node.else_clause`` is not ``None``, execute the
             else clause's body.

        HINT:
          • Use ``self._is_truthy(self._eval(clause.condition))`` to test
            each elif condition.
          • Use ``self._exec_block(clause.body)`` to execute a clause's
            body.
          • Remember to ``return`` after executing a branch so that
            subsequent branches are skipped.
        """
        # Evaluate the primary 'if' condition.
        if self._is_truthy(self._eval(node.condition)):
            self._exec_block(node.body)
            return

        # ── TODO: Evaluate elif clauses (exercise 1) ──
        # for clause in node.elif_clauses:
        #     ...

        # ── TODO: Evaluate else clause (exercise 2) ──
        # if node.else_clause is not None:
        #     ...

    def _exec_block(self, statements: tuple[ASTNode, ...]) -> None:
        """Execute every statement in a block sequentially."""
        for stmt in statements:
            self._exec_statement(stmt)

    # -----------------------------------------------------------------------
    # Expression evaluation (Visitor dispatcher)
    # -----------------------------------------------------------------------

    def _eval(self, node: ASTNode) -> Value:
        """
        Central dispatcher — evaluates any expression node by delegating
        to the appropriate ``_eval_*`` visitor method.
        """
        if isinstance(node, IntLiteral):
            return node.value
        if isinstance(node, FloatLiteral):
            return node.value
        if isinstance(node, CharLiteral):
            return node.value
        if isinstance(node, BoolLiteral):
            return node.value
        if isinstance(node, Variable):
            return self._eval_variable(node)
        if isinstance(node, BinaryOp):
            return self._eval_binary_op(node)
        if isinstance(node, UnaryOp):
            return self._eval_unary_op(node)
        if isinstance(node, Comparison):
            return self._eval_comparison(node)
        if isinstance(node, BooleanOp):
            return self._eval_boolean_op(node)
        if isinstance(node, NotOp):
            return self._eval_not_op(node)

        raise EvalError(f"Cannot evaluate node: {type(node).__name__}")

    # -----------------------------------------------------------------------
    # Visitor methods
    # -----------------------------------------------------------------------

    def _eval_variable(self, node: Variable) -> Value:
        """Look up a variable in the global store."""
        if node.name not in self.variables:
            raise EvalError(f"Undefined variable: '{node.name}'")
        return self.variables[node.name]

    def _eval_binary_op(self, node: BinaryOp) -> Value:
        """
        Evaluate a binary arithmetic operation.

        Implemented operators: ``+``, ``-``, ``*``, ``/``
        (including division-by-zero guard for ``/``).

        TODO (Student Exercise — implement the remaining operators):
        ─────────────────────────────────────────────────────────────
          1. **Floor division (``//``)**:
             Return ``left // right``.  Guard against division by zero
             just like true division.

          2. **Modulo (``%``)**:
             Return ``left % right``.  Guard against modulo by zero
             (raise ``EvalError("Modulo by zero")``).

          3. **Exponentiation (``**``)**:
             Return ``left ** right``.  No special guards are needed
             for the scope of this project, but you may optionally
             handle ``0 ** negative`` which raises ``ZeroDivisionError``
             in Python.

        HINT: Follow the pattern of the existing ``+``, ``-``, ``*``,
        ``/`` branches.  Use Python's built-in operators directly;
        Python handles int/float promotion automatically.
        """
        left = self._eval(node.left)
        right = self._eval(node.right)

        match node.op:
            case "+":
                return left + right
            case "-":
                return left - right
            case "*":
                return left * right
            case "/":
                if right == 0:
                    raise EvalError("Division by zero")
                return left / right

            # ── TODO: Floor division '//' (exercise 1) ──
            # case "//":
            #     ...

            # ── TODO: Modulo '%' (exercise 2) ──
            # case "%":
            #     ...

            # ── TODO: Exponentiation '**' (exercise 3) ──
            # case "**":
            #     ...

            case _:
                raise EvalError(f"Unknown binary operator: '{node.op}'")

    def _eval_unary_op(self, node: UnaryOp) -> Value:
        """Evaluate a unary ``+`` or ``-`` prefix operator."""
        operand = self._eval(node.operand)
        if node.op == "+":
            return +operand
        if node.op == "-":
            return -operand
        raise EvalError(f"Unknown unary operator: '{node.op}'")

    def _eval_comparison(self, node: Comparison) -> bool:
        """
        Evaluate a comparison expression and return a boolean.

        Implemented operators: ``==``, ``!=``

        TODO (Student Exercise — implement the remaining operators):
        ─────────────────────────────────────────────────────────────
          1. ``<``  — less than
          2. ``>``  — greater than
          3. ``<=`` — less than or equal
          4. ``>=`` — greater than or equal

        HINT: Use Python's built-in comparison operators.  They work
        correctly for int, float, str (character), and bool values.
        Follow the ``==`` / ``!=`` pattern exactly.
        """
        left = self._eval(node.left)
        right = self._eval(node.right)

        match node.op:
            case "==":
                return left == right
            case "!=":
                return left != right

            # ── TODO: Less than '<' (exercise 1) ──
            # case "<":
            #     ...

            # ── TODO: Greater than '>' (exercise 2) ──
            # case ">":
            #     ...

            # ── TODO: Less than or equal '<=' (exercise 3) ──
            # case "<=":
            #     ...

            # ── TODO: Greater than or equal '>=' (exercise 4) ──
            # case ">=":
            #     ...

            case _:
                raise EvalError(f"Unknown comparison operator: '{node.op}'")

    def _eval_boolean_op(self, node: BooleanOp) -> bool:
        """
        Evaluate ``and`` / ``or`` with short-circuit semantics.

        TODO (Student Exercise):
        ────────────────────────
        Implement short-circuit evaluation for ``and`` and ``or``:

          • ``and``: If the left operand is falsy, return ``False``
            immediately **without evaluating the right operand**.
            Otherwise, return the truthiness of the right operand.

          • ``or``: If the left operand is truthy, return ``True``
            immediately **without evaluating the right operand**.
            Otherwise, return the truthiness of the right operand.

        HINT: Use ``self._is_truthy(...)`` to convert values to bool.
        Evaluate ``self._eval(node.left)`` first, check its truthiness,
        and only evaluate ``self._eval(node.right)`` if needed.
        """
        # ── TODO: Implement short-circuit 'and' / 'or' ──
        raise EvalError(
            f"Boolean operator '{node.op}' is not yet implemented. "
            "Complete the TODO in _eval_boolean_op."
        )

    def _eval_not_op(self, node: NotOp) -> bool:
        """Evaluate ``not expr`` — returns the boolean negation."""
        operand = self._eval(node.operand)
        return not self._is_truthy(operand)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _is_truthy(value: Value) -> bool:
        """
        Determine the truthiness of a runtime value.

        Rules (matching Python semantics):
          • ``False``, ``0``, ``0.0`` → falsy
          • Everything else → truthy (including non-empty characters)
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return bool(value)


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def evaluate(program: Program) -> tuple[str, dict[str, Value]]:
    """
    Execute a mini-Python program and return its output and variable store.

    Parameters
    ----------
    program : Program
        The root AST node (from ``lexer_parser.parse``).

    Returns
    -------
    tuple[str, dict[str, Value]]
        A 2-tuple of (captured_output, variables_dict).
    """
    evaluator = Evaluator()
    output = evaluator.execute(program)
    return output, evaluator.variables
