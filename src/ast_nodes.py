"""
ast_nodes.py — Abstract Syntax Tree Node Definitions
=====================================================

Every node in the AST is a frozen ``dataclass`` so that:
  1. Nodes are immutable after construction (reduces bugs).
  2. ``__eq__`` / ``__hash__`` are auto-generated, making testing easier.
  3. Type hints provide self-documentation.

The node hierarchy:
    ASTNode  (base)
    ├── Program
    ├── Assignment
    ├── IndexAssignment
    ├── PrintStatement
    ├── IfStatement
    ├── ElifClause
    ├── ElseClause
    ├── WhileStatement
    ├── ForStatement
    ├── DoWhileStatement
    ├── BinaryOp
    ├── UnaryOp
    ├── Comparison
    ├── BooleanOp
    ├── NotOp
    ├── IntLiteral
    ├── FloatLiteral
    ├── CharLiteral
    ├── BoolLiteral
    ├── Variable
    ├── ArrayLiteral
    ├── IndexAccess
    ├── RangeExpression
    └── LenExpression
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ASTNode:
    """Abstract base for every AST node."""
    pass


# ---------------------------------------------------------------------------
# Literals
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IntLiteral(ASTNode):
    """An integer literal, e.g. ``42``."""
    value: int


@dataclass(frozen=True)
class FloatLiteral(ASTNode):
    """A floating-point literal, e.g. ``3.14``."""
    value: float


@dataclass(frozen=True)
class CharLiteral(ASTNode):
    """A character literal, e.g. ``'a'``.  Stored *without* surrounding quotes."""
    value: str  # always exactly one character


@dataclass(frozen=True)
class BoolLiteral(ASTNode):
    """A boolean literal — ``True`` or ``False``."""
    value: bool


# ---------------------------------------------------------------------------
# Variable Reference
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Variable(ASTNode):
    """A reference to a named variable in the global scope."""
    name: str


# ---------------------------------------------------------------------------
# Array & Indexing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArrayLiteral(ASTNode):
    """An array literal, e.g. ``[1, 2, 3]``."""
    elements: tuple[ASTNode, ...]


@dataclass(frozen=True)
class IndexAccess(ASTNode):
    """Array index access, e.g. ``arr[0]``."""
    array: ASTNode
    index: ASTNode


@dataclass(frozen=True)
class RangeExpression(ASTNode):
    """Built-in ``range(...)`` call producing an array of integers."""
    start: ASTNode | None
    stop: ASTNode
    step: ASTNode | None


@dataclass(frozen=True)
class LenExpression(ASTNode):
    """Built-in ``len(expr)`` returning the length of an array."""
    argument: ASTNode


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BinaryOp(ASTNode):
    """A binary arithmetic operation (``+  -  *  /  //  %  **``)."""
    op: str            # one of: '+', '-', '*', '/', '//', '%', '**'
    left: ASTNode
    right: ASTNode


@dataclass(frozen=True)
class UnaryOp(ASTNode):
    """A unary prefix operation (``+expr`` or ``-expr``)."""
    op: str            # '+' or '-'
    operand: ASTNode


@dataclass(frozen=True)
class Comparison(ASTNode):
    """A comparison expression (``==  !=  <  >  <=  >=``)."""
    op: str            # one of: '==', '!=', '<', '>', '<=', '>='
    left: ASTNode
    right: ASTNode


@dataclass(frozen=True)
class BooleanOp(ASTNode):
    """A boolean binary expression (``and``, ``or``)."""
    op: str            # 'and' or 'or'
    left: ASTNode
    right: ASTNode


@dataclass(frozen=True)
class NotOp(ASTNode):
    """Boolean negation (``not expr``)."""
    operand: ASTNode


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Assignment(ASTNode):
    """Variable assignment: ``<name> = <expression>``."""
    name: str
    value: ASTNode


@dataclass(frozen=True)
class IndexAssignment(ASTNode):
    """Array index assignment: ``arr[i] = expr``."""
    name: str
    index: ASTNode
    value: ASTNode


@dataclass(frozen=True)
class PrintStatement(ASTNode):
    """``print(<expression>)``."""
    expression: ASTNode


@dataclass(frozen=True)
class ElifClause(ASTNode):
    """A single ``elif`` branch."""
    condition: ASTNode
    body: tuple[ASTNode, ...]


@dataclass(frozen=True)
class ElseClause(ASTNode):
    """The ``else`` branch."""
    body: tuple[ASTNode, ...]


@dataclass(frozen=True)
class IfStatement(ASTNode):
    """
    An ``if / elif / else`` compound statement.

    Attributes:
        condition:     The boolean expression for the ``if`` test.
        body:          Tuple of statements in the ``if`` block.
        elif_clauses:  Zero or more ``ElifClause`` nodes.
        else_clause:   An optional ``ElseClause`` node.
    """
    condition: ASTNode
    body: tuple[ASTNode, ...]
    elif_clauses: tuple[ElifClause, ...] = field(default_factory=tuple)
    else_clause: ElseClause | None = None


@dataclass(frozen=True)
class WhileStatement(ASTNode):
    """A ``while`` loop: ``while <condition>: <body>``."""
    condition: ASTNode
    body: tuple[ASTNode, ...]


@dataclass(frozen=True)
class ForStatement(ASTNode):
    """A ``for`` loop: ``for <variable> in <iterable>: <body>``."""
    variable: str
    iterable: ASTNode
    body: tuple[ASTNode, ...]


@dataclass(frozen=True)
class DoWhileStatement(ASTNode):
    """A ``do-while`` loop: ``do: <body> while <condition>``."""
    condition: ASTNode
    body: tuple[ASTNode, ...]


@dataclass(frozen=True)
class Program(ASTNode):
    """The root of the AST — a sequence of top-level statements."""
    statements: tuple[ASTNode, ...]
