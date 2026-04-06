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
  variable access, index out of bounds, etc.).
"""

from __future__ import annotations

import io
from typing import Any

from src.ast_nodes import (
    ASTNode,
    ArrayLiteral,
    Assignment,
    BinaryOp,
    BooleanOp,
    BoolLiteral,
    CharLiteral,
    Comparison,
    DoWhileStatement,
    ElifClause,
    ElseClause,
    FloatLiteral,
    ForStatement,
    IfStatement,
    IndexAccess,
    IndexAssignment,
    IntLiteral,
    LenExpression,
    NotOp,
    PrintStatement,
    Program,
    RangeExpression,
    UnaryOp,
    Variable,
    WhileStatement,
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

Value = int | float | str | bool | list  # str is always a single character


# ---------------------------------------------------------------------------
# Safety limits
# ---------------------------------------------------------------------------

MAX_ITERATIONS = 100_000  # Prevent infinite loops


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
        Captures ``print`` output.
    """

    def __init__(self) -> None:
        self.variables: dict[str, Value] = {}
        self.output_buffer: io.StringIO = io.StringIO()

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def execute(self, program: Program) -> str:
        for stmt in program.statements:
            self._exec_statement(stmt)
        return self.output_buffer.getvalue()

    def get_variable(self, name: str) -> Value:
        if name not in self.variables:
            raise EvalError(f"Undefined variable: '{name}'")
        return self.variables[name]

    # -----------------------------------------------------------------------
    # Statement execution
    # -----------------------------------------------------------------------

    def _exec_statement(self, node: ASTNode) -> None:
        if isinstance(node, Assignment):
            self._exec_assignment(node)
        elif isinstance(node, IndexAssignment):
            self._exec_index_assignment(node)
        elif isinstance(node, PrintStatement):
            self._exec_print(node)
        elif isinstance(node, IfStatement):
            self._exec_if(node)
        elif isinstance(node, WhileStatement):
            self._exec_while(node)
        elif isinstance(node, ForStatement):
            self._exec_for(node)
        elif isinstance(node, DoWhileStatement):
            self._exec_do_while(node)
        else:
            raise EvalError(f"Unknown statement type: {type(node).__name__}")

    def _exec_assignment(self, node: Assignment) -> None:
        value = self._eval(node.value)
        self.variables[node.name] = value

    def _exec_index_assignment(self, node: IndexAssignment) -> None:
        if node.name not in self.variables:
            raise EvalError(f"Undefined variable: '{node.name}'")
        arr = self.variables[node.name]
        if not isinstance(arr, list):
            raise EvalError(f"Variable '{node.name}' is not an array")
        index = self._eval(node.index)
        if not isinstance(index, int):
            raise EvalError("Array index must be an integer")
        if index < 0 or index >= len(arr):
            raise EvalError(f"Index {index} out of bounds for array of length {len(arr)}")
        value = self._eval(node.value)
        arr[index] = value

    def _exec_print(self, node: PrintStatement) -> None:
        value = self._eval(node.expression)
        self.output_buffer.write(f"{self._format_value(value)}\n")

    def _exec_if(self, node: IfStatement) -> None:
        if self._is_truthy(self._eval(node.condition)):
            self._exec_block(node.body)
            return

        for clause in node.elif_clauses:
            if self._is_truthy(self._eval(clause.condition)):
                self._exec_block(clause.body)
                return

        if node.else_clause is not None:
            self._exec_block(node.else_clause.body)

    def _exec_while(self, node: WhileStatement) -> None:
        iterations = 0
        while self._is_truthy(self._eval(node.condition)):
            self._exec_block(node.body)
            iterations += 1
            if iterations > MAX_ITERATIONS:
                raise EvalError(
                    f"While loop exceeded maximum iterations ({MAX_ITERATIONS}). "
                    "Possible infinite loop."
                )

    def _exec_for(self, node: ForStatement) -> None:
        iterable = self._eval(node.iterable)
        if not isinstance(iterable, list):
            raise EvalError("'for' loop requires an iterable (array or range)")
        iterations = 0
        for item in iterable:
            self.variables[node.variable] = item
            self._exec_block(node.body)
            iterations += 1
            if iterations > MAX_ITERATIONS:
                raise EvalError(
                    f"For loop exceeded maximum iterations ({MAX_ITERATIONS}). "
                    "Possible infinite loop."
                )

    def _exec_do_while(self, node: DoWhileStatement) -> None:
        iterations = 0
        while True:
            self._exec_block(node.body)
            iterations += 1
            if iterations > MAX_ITERATIONS:
                raise EvalError(
                    f"Do-while loop exceeded maximum iterations ({MAX_ITERATIONS}). "
                    "Possible infinite loop."
                )
            if not self._is_truthy(self._eval(node.condition)):
                break

    def _exec_block(self, statements: tuple[ASTNode, ...]) -> None:
        for stmt in statements:
            self._exec_statement(stmt)

    # -----------------------------------------------------------------------
    # Expression evaluation (Visitor dispatcher)
    # -----------------------------------------------------------------------

    def _eval(self, node: ASTNode) -> Value:
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
        if isinstance(node, ArrayLiteral):
            return self._eval_array_literal(node)
        if isinstance(node, IndexAccess):
            return self._eval_index_access(node)
        if isinstance(node, RangeExpression):
            return self._eval_range(node)
        if isinstance(node, LenExpression):
            return self._eval_len(node)

        raise EvalError(f"Cannot evaluate node: {type(node).__name__}")

    # -----------------------------------------------------------------------
    # Visitor methods
    # -----------------------------------------------------------------------

    def _eval_variable(self, node: Variable) -> Value:
        if node.name not in self.variables:
            raise EvalError(f"Undefined variable: '{node.name}'")
        return self.variables[node.name]

    def _eval_binary_op(self, node: BinaryOp) -> Value:
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
            case "//":
                if right == 0:
                    raise EvalError("Floor division by zero")
                return left // right
            case "%":
                if right == 0:
                    raise EvalError("Modulo by zero")
                return left % right
            case "**":
                return left ** right
            case _:
                raise EvalError(f"Unknown binary operator: '{node.op}'")

    def _eval_unary_op(self, node: UnaryOp) -> Value:
        operand = self._eval(node.operand)
        if node.op == "+":
            return +operand
        if node.op == "-":
            return -operand
        raise EvalError(f"Unknown unary operator: '{node.op}'")

    def _eval_comparison(self, node: Comparison) -> bool:
        left = self._eval(node.left)
        right = self._eval(node.right)

        match node.op:
            case "==":
                return left == right
            case "!=":
                return left != right
            case "<":
                return left < right
            case ">":
                return left > right
            case "<=":
                return left <= right
            case ">=":
                return left >= right
            case _:
                raise EvalError(f"Unknown comparison operator: '{node.op}'")

    def _eval_boolean_op(self, node: BooleanOp) -> bool:
        left = self._eval(node.left)
        if node.op == "and":
            if not self._is_truthy(left):
                return False
            return self._is_truthy(self._eval(node.right))
        elif node.op == "or":
            if self._is_truthy(left):
                return True
            return self._is_truthy(self._eval(node.right))
        raise EvalError(f"Unknown boolean operator: '{node.op}'")

    def _eval_not_op(self, node: NotOp) -> bool:
        operand = self._eval(node.operand)
        return not self._is_truthy(operand)

    def _eval_array_literal(self, node: ArrayLiteral) -> list:
        return [self._eval(elem) for elem in node.elements]

    def _eval_index_access(self, node: IndexAccess) -> Value:
        arr = self._eval(node.array)
        if not isinstance(arr, list):
            raise EvalError("Index access requires an array")
        index = self._eval(node.index)
        if not isinstance(index, int):
            raise EvalError("Array index must be an integer")
        if index < 0 or index >= len(arr):
            raise EvalError(f"Index {index} out of bounds for array of length {len(arr)}")
        return arr[index]

    def _eval_range(self, node: RangeExpression) -> list:
        stop = self._eval(node.stop)
        start = self._eval(node.start) if node.start is not None else 0
        step = self._eval(node.step) if node.step is not None else 1
        if not isinstance(start, int) or not isinstance(stop, int) or not isinstance(step, int):
            raise EvalError("range() arguments must be integers")
        if step == 0:
            raise EvalError("range() step argument must not be zero")
        return list(range(start, stop, step))

    def _eval_len(self, node: LenExpression) -> int:
        arg = self._eval(node.argument)
        if not isinstance(arg, list):
            raise EvalError("len() requires an array argument")
        return len(arg)

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _is_truthy(value: Value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
            return len(value) > 0
        return bool(value)

    @staticmethod
    def _format_value(value: Value) -> str:
        """Format a runtime value for print output."""
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, list):
            parts = ", ".join(Evaluator._format_value(v) for v in value)
            return f"[{parts}]"
        return str(value)


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def evaluate(program: Program) -> tuple[str, dict[str, Value]]:
    """
    Execute a mini-Python program and return its output and variable store.
    """
    evaluator = Evaluator()
    output = evaluator.execute(program)
    return output, evaluator.variables
