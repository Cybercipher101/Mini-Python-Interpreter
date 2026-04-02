"""
semantic_analyzer.py — Middleware: Symbol Table & Type Checker
==============================================================

This module sits between the parser (frontend) and evaluator (backend).
It walks the AST **before** execution to:

  1. Build a **Symbol Table** — a mapping of variable names to their
     inferred types (``int``, ``float``, ``char``, ``bool``).
  2. **Type-check** expressions so that type errors are caught at
     analysis time rather than at runtime.

Design Decisions
----------------
* **Single global scope**: the symbol table is a flat ``dict``.
* **Type inference**: a variable's type is inferred from its first
  assignment.  Re-assignment to a different type is flagged as an error.
* **Arithmetic promotion**: ``int + float → float`` (standard widening).
* **Character type**: characters may be compared (``==``, ``<``, etc.) but
  arithmetic on characters is **not** permitted.

Error Reporting
---------------
All semantic errors are raised as ``SemanticError`` with a human-readable
message.  The CLI layer catches these and presents them to the user.

TODO Blocks for Students
-------------------------
Several type-checking rules in ``_check_binary_op`` and
``_check_comparison`` are left as TODO exercises.  Search for ``TODO``
to find them.
"""

from __future__ import annotations

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

class SemanticError(Exception):
    """Raised when the semantic analyzer detects a type or scope error."""
    pass


# ---------------------------------------------------------------------------
# Type constants used by the analyzer
# ---------------------------------------------------------------------------

# We represent types as simple strings for readability and easy comparison.
INT: str = "int"
FLOAT: str = "float"
CHAR: str = "char"
BOOL: str = "bool"

# Set of numeric types (eligible for arithmetic promotion).
NUMERIC_TYPES: set[str] = {INT, FLOAT}


# ---------------------------------------------------------------------------
# Semantic Analyzer
# ---------------------------------------------------------------------------

class SemanticAnalyzer:
    """
    Performs a single pre-execution pass over the AST.

    Attributes
    ----------
    symbol_table : dict[str, str]
        Maps variable names to their inferred type strings.
    errors : list[str]
        Accumulated error messages (the analyzer tries to report as many
        errors as possible in one pass rather than stopping at the first).
    """

    def __init__(self, symbol_table: dict[str, str] | None = None) -> None:
        self.symbol_table: dict[str, str] = symbol_table if symbol_table is not None else {}
        self.errors: list[str] = []

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def analyze(self, program: Program) -> None:
        """
        Analyze the full program.  Raises ``SemanticError`` if any errors
        were found.

        Parameters
        ----------
        program : Program
            The root AST node.

        Raises
        ------
        SemanticError
            With a combined message listing all errors detected.
        """
        for stmt in program.statements:
            self._analyze_statement(stmt)

        if self.errors:
            raise SemanticError(
                "Semantic analysis found the following errors:\n"
                + "\n".join(f"  • {e}" for e in self.errors)
            )

    # -----------------------------------------------------------------------
    # Statement analysis
    # -----------------------------------------------------------------------

    def _analyze_statement(self, node: ASTNode) -> None:
        """Dispatch a statement node to the appropriate handler."""
        if isinstance(node, Assignment):
            self._analyze_assignment(node)
        elif isinstance(node, PrintStatement):
            self._analyze_print(node)
        elif isinstance(node, IfStatement):
            self._analyze_if(node)
        else:
            self.errors.append(f"Unknown statement type: {type(node).__name__}")

    def _analyze_assignment(self, node: Assignment) -> None:
        """
        Check an assignment statement.

        * Infer the type of the right-hand side expression.
        * If the variable has not been seen before, record its type.
        * If the variable *has* been seen, verify that the new type is
          compatible (same type or valid numeric promotion).
        """
        rhs_type = self._infer_type(node.value)
        if rhs_type is None:
            return  # type inference already recorded an error

        if node.name not in self.symbol_table:
            # First assignment — register the variable.
            self.symbol_table[node.name] = rhs_type
        else:
            existing = self.symbol_table[node.name]
            # Allow int → float promotion on reassignment.
            if existing == rhs_type:
                pass  # same type — OK
            elif {existing, rhs_type} == {INT, FLOAT}:
                # Promote the stored type to float.
                self.symbol_table[node.name] = FLOAT
            else:
                self.errors.append(
                    f"Type mismatch: variable '{node.name}' was declared as "
                    f"'{existing}' but is being assigned '{rhs_type}'."
                )

    def _analyze_print(self, node: PrintStatement) -> None:
        """Type-check the expression inside ``print(...)``."""
        self._infer_type(node.expression)

    def _analyze_if(self, node: IfStatement) -> None:
        """
        Type-check an if / elif / else compound statement.

        The condition of each ``if`` and ``elif`` must be boolean-compatible.
        """
        cond_type = self._infer_type(node.condition)
        if cond_type is not None and cond_type not in (BOOL, INT, FLOAT):
            self.errors.append(
                f"Condition in 'if' must be bool-compatible, got '{cond_type}'."
            )

        for stmt in node.body:
            self._analyze_statement(stmt)

        for elif_clause in node.elif_clauses:
            self._analyze_elif(elif_clause)

        if node.else_clause is not None:
            self._analyze_else(node.else_clause)

    def _analyze_elif(self, node: ElifClause) -> None:
        cond_type = self._infer_type(node.condition)
        if cond_type is not None and cond_type not in (BOOL, INT, FLOAT):
            self.errors.append(
                f"Condition in 'elif' must be bool-compatible, got '{cond_type}'."
            )
        for stmt in node.body:
            self._analyze_statement(stmt)

    def _analyze_else(self, node: ElseClause) -> None:
        for stmt in node.body:
            self._analyze_statement(stmt)

    # -----------------------------------------------------------------------
    # Expression type inference
    # -----------------------------------------------------------------------

    def _infer_type(self, node: ASTNode) -> str | None:
        """
        Recursively infer the result type of an expression node.

        Returns the type string, or ``None`` if a type error was recorded.
        """
        if isinstance(node, IntLiteral):
            return INT
        if isinstance(node, FloatLiteral):
            return FLOAT
        if isinstance(node, CharLiteral):
            return CHAR
        if isinstance(node, BoolLiteral):
            return BOOL

        if isinstance(node, Variable):
            return self._infer_variable(node)
        if isinstance(node, BinaryOp):
            return self._check_binary_op(node)
        if isinstance(node, UnaryOp):
            return self._check_unary_op(node)
        if isinstance(node, Comparison):
            return self._check_comparison(node)
        if isinstance(node, BooleanOp):
            return self._check_boolean_op(node)
        if isinstance(node, NotOp):
            return self._check_not_op(node)

        self.errors.append(f"Cannot infer type for node: {type(node).__name__}")
        return None

    def _infer_variable(self, node: Variable) -> str | None:
        """Look up a variable's type in the symbol table."""
        if node.name in self.symbol_table:
            return self.symbol_table[node.name]
        self.errors.append(f"Undefined variable: '{node.name}'.")
        return None

    # -----------------------------------------------------------------------
    # Operator type rules
    # -----------------------------------------------------------------------

    def _check_binary_op(self, node: BinaryOp) -> str | None:
        """
        Enforce type rules for binary arithmetic operators.

        Implemented rules:
          • int   ○ int   → int     (for +, -, *, //, %, **)
          • int   / int   → float   (true division always yields float)
          • float ○ float → float
          • int   ○ float → float   (numeric promotion)

        TODO (Student Exercise — implement the remaining rules):
        ──────────────────────────────────────────────────────────
        The following cases must be handled:

          1. **Modulo with floats**: ``float % float → float`` and
             ``int % float → float``.  Currently only ``int % int``
             is handled.  Add the promotion logic for ``%`` so that
             if *either* operand is a float the result is float.

          2. **Floor division with floats**: ``float // float → float``
             (Python returns a float for ``3.0 // 2.0``).  Add this
             promotion rule alongside the int rule.

          3. **Power with mixed types**: ``int ** float`` should yield
             ``float``, and ``float ** int`` should also yield ``float``.
             Currently ``**`` only handles int**int → int.

          4. **Error on char operands**: If *either* operand is ``char``,
             emit an error: ``"Arithmetic on characters is not supported."``
             Currently char operands silently fall through.

          5. **Error on bool operands**: If *either* operand is ``bool``,
             emit an error: ``"Arithmetic on booleans is not supported."``
             Add this guard before the numeric checks.

        HINT: Check `left_type` and `right_type` against the CHAR and
        BOOL constants, and call ``self.errors.append(...)`` for each
        invalid case.  Return ``None`` to indicate an error.
        """
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)

        if left_type is None or right_type is None:
            return None

        # ── TODO: Guard against char operands (exercise 4) ──
        # if left_type == CHAR or right_type == CHAR:
        #     ...
        #     return None

        # ── TODO: Guard against bool operands (exercise 5) ──
        # if left_type == BOOL or right_type == BOOL:
        #     ...
        #     return None

        # Both operands are int
        if left_type == INT and right_type == INT:
            if node.op == "/":
                return FLOAT        # true division always produces float
            return INT

        # Both operands are float
        if left_type == FLOAT and right_type == FLOAT:
            return FLOAT

        # Mixed int/float — promotion to float
        if {left_type, right_type} == {INT, FLOAT}:
            return FLOAT

        # ── TODO: Handle remaining promotion cases (exercises 1–3) ──
        # For now, fall through to error.

        self.errors.append(
            f"Unsupported operand types for '{node.op}': "
            f"'{left_type}' and '{right_type}'."
        )
        return None

    def _check_unary_op(self, node: UnaryOp) -> str | None:
        """
        Enforce type rules for unary ``+`` / ``-``.

        Only numeric types (int, float) are valid operands.
        """
        operand_type = self._infer_type(node.operand)
        if operand_type is None:
            return None

        if operand_type in NUMERIC_TYPES:
            return operand_type

        self.errors.append(
            f"Unary '{node.op}' not supported for type '{operand_type}'."
        )
        return None

    def _check_comparison(self, node: Comparison) -> str | None:
        """
        Enforce type rules for comparison operators.

        Implemented rules:
          • numeric ○ numeric → bool   (int/float comparisons, with promotion)
          • char    ○ char    → bool   (lexicographic comparison)

        TODO (Student Exercise — implement the remaining rules):
        ──────────────────────────────────────────────────────────
          1. **Bool-to-bool comparison for == and !=**:
             ``bool == bool → bool`` and ``bool != bool → bool`` are valid.
             Other comparisons on bools (``<``, ``>``, etc.) should emit:
             ``"Ordering comparisons on booleans are not supported."``

          2. **Cross-type comparison error**:
             Comparing a ``char`` to an ``int`` or ``float`` should emit:
             ``"Cannot compare '{left_type}' with '{right_type}'."``
             Currently the function falls through to a generic error.
             Make this error message explicit for cross-type cases.

        HINT: Add checks for ``left_type == BOOL`` and handle the operator
        set ``{'==', '!='}`` separately from ordering operators.
        """
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)

        if left_type is None or right_type is None:
            return None

        # Numeric comparisons (int/float, with promotion)
        if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
            return BOOL

        # Char-to-char comparison
        if left_type == CHAR and right_type == CHAR:
            return BOOL

        # ── TODO: Bool-to-bool equality comparison (exercise 1) ──
        # ── TODO: Explicit cross-type error (exercise 2) ──

        self.errors.append(
            f"Cannot compare '{left_type}' with '{right_type}'."
        )
        return None

    def _check_boolean_op(self, node: BooleanOp) -> str | None:
        """
        Enforce type rules for ``and`` / ``or``.

        Both operands must be bool-compatible (bool, int, or float —
        Python treats nonzero numbers as truthy).
        """
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)

        if left_type is None or right_type is None:
            return None

        bool_compatible = {BOOL, INT, FLOAT}
        if left_type in bool_compatible and right_type in bool_compatible:
            return BOOL

        self.errors.append(
            f"Operands of '{node.op}' must be bool-compatible, "
            f"got '{left_type}' and '{right_type}'."
        )
        return None

    def _check_not_op(self, node: NotOp) -> str | None:
        """
        Enforce type rules for ``not``.

        The operand must be bool-compatible.
        """
        operand_type = self._infer_type(node.operand)
        if operand_type is None:
            return None

        if operand_type in {BOOL, INT, FLOAT}:
            return BOOL

        self.errors.append(
            f"Operand of 'not' must be bool-compatible, got '{operand_type}'."
        )
        return None


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def analyze(program: Program, symbol_table: dict[str, str] | None = None) -> dict[str, str]:
    """
    Run semantic analysis on a parsed program.

    Parameters
    ----------
    program : Program
        The root AST node (from ``lexer_parser.parse``).
    symbol_table : dict[str, str], optional
        An existing symbol table to build upon (for REPL persistence).
        If ``None``, a fresh symbol table is created.

    Returns
    -------
    dict[str, str]
        The symbol table mapping variable names to type strings.

    Raises
    ------
    SemanticError
        If any semantic errors are detected.
    """
    analyzer = SemanticAnalyzer(symbol_table=symbol_table)
    analyzer.analyze(program)
    return analyzer.symbol_table
