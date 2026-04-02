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
    ├── PrintStatement
    ├── IfStatement
    ├── ElifClause
    ├── ElseClause
    ├── BinaryOp
    ├── UnaryOp
    ├── Comparison
    ├── BooleanOp
    ├── NotOp
    ├── IntLiteral
    ├── FloatLiteral
    ├── CharLiteral
    ├── BoolLiteral
    └── Variable
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
class Program(ASTNode):
    """The root of the AST — a sequence of top-level statements."""
    statements: tuple[ASTNode, ...]
