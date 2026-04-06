"""
semantic_analyzer.py — Middleware: Symbol Table & Type Checker
==============================================================

This module sits between the parser (frontend) and evaluator (backend).
It walks the AST **before** execution to:

  1. Build a **Symbol Table** — a mapping of variable names to their
     inferred types (``int``, ``float``, ``char``, ``bool``, ``array``).
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
* **Array type**: arrays are a generic ``array`` type; element types are
  not tracked statically.
* **ANY type**: used for index-access results and loop variables when the
  element type is unknown.  ANY is compatible with all types.
"""

from __future__ import annotations

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

class SemanticError(Exception):
    """Raised when the semantic analyzer detects a type or scope error."""
    pass


# ---------------------------------------------------------------------------
# Type constants used by the analyzer
# ---------------------------------------------------------------------------

INT: str = "int"
FLOAT: str = "float"
CHAR: str = "char"
BOOL: str = "bool"
ARRAY: str = "array"
ANY: str = "any"

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
        Accumulated error messages.
    """

    def __init__(self, symbol_table: dict[str, str] | None = None) -> None:
        self.symbol_table: dict[str, str] = symbol_table if symbol_table is not None else {}
        self.errors: list[str] = []

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def analyze(self, program: Program) -> None:
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
        elif isinstance(node, IndexAssignment):
            self._analyze_index_assignment(node)
        elif isinstance(node, PrintStatement):
            self._analyze_print(node)
        elif isinstance(node, IfStatement):
            self._analyze_if(node)
        elif isinstance(node, WhileStatement):
            self._analyze_while(node)
        elif isinstance(node, ForStatement):
            self._analyze_for(node)
        elif isinstance(node, DoWhileStatement):
            self._analyze_do_while(node)
        else:
            self.errors.append(f"Unknown statement type: {type(node).__name__}")

    def _analyze_assignment(self, node: Assignment) -> None:
        rhs_type = self._infer_type(node.value)
        if rhs_type is None:
            return

        if node.name not in self.symbol_table:
            self.symbol_table[node.name] = rhs_type
        else:
            existing = self.symbol_table[node.name]
            if existing == rhs_type:
                pass
            elif ANY in (existing, rhs_type):
                pass  # ANY is compatible with everything
            elif {existing, rhs_type} == {INT, FLOAT}:
                self.symbol_table[node.name] = FLOAT
            else:
                self.errors.append(
                    f"Type mismatch: variable '{node.name}' was declared as "
                    f"'{existing}' but is being assigned '{rhs_type}'."
                )

    def _analyze_index_assignment(self, node: IndexAssignment) -> None:
        """Check array index assignment: arr[i] = expr."""
        if node.name not in self.symbol_table:
            self.errors.append(f"Undefined variable: '{node.name}'.")
            return
        var_type = self.symbol_table[node.name]
        if var_type != ARRAY and var_type != ANY:
            self.errors.append(
                f"Cannot index into variable '{node.name}' of type '{var_type}'."
            )
        self._infer_type(node.index)
        self._infer_type(node.value)

    def _analyze_print(self, node: PrintStatement) -> None:
        self._infer_type(node.expression)

    def _analyze_if(self, node: IfStatement) -> None:
        cond_type = self._infer_type(node.condition)
        if cond_type is not None and cond_type not in (BOOL, INT, FLOAT, ANY):
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
        if cond_type is not None and cond_type not in (BOOL, INT, FLOAT, ANY):
            self.errors.append(
                f"Condition in 'elif' must be bool-compatible, got '{cond_type}'."
            )
        for stmt in node.body:
            self._analyze_statement(stmt)

    def _analyze_else(self, node: ElseClause) -> None:
        for stmt in node.body:
            self._analyze_statement(stmt)

    def _analyze_while(self, node: WhileStatement) -> None:
        cond_type = self._infer_type(node.condition)
        if cond_type is not None and cond_type not in (BOOL, INT, FLOAT, ANY):
            self.errors.append(
                f"Condition in 'while' must be bool-compatible, got '{cond_type}'."
            )
        for stmt in node.body:
            self._analyze_statement(stmt)

    def _analyze_for(self, node: ForStatement) -> None:
        iter_type = self._infer_type(node.iterable)
        if iter_type is not None and iter_type not in (ARRAY, ANY):
            self.errors.append(
                f"'for' loop requires an iterable (array/range), got '{iter_type}'."
            )
        # Register loop variable — type is ANY (element type unknown statically)
        self.symbol_table[node.variable] = ANY
        for stmt in node.body:
            self._analyze_statement(stmt)

    def _analyze_do_while(self, node: DoWhileStatement) -> None:
        for stmt in node.body:
            self._analyze_statement(stmt)
        cond_type = self._infer_type(node.condition)
        if cond_type is not None and cond_type not in (BOOL, INT, FLOAT, ANY):
            self.errors.append(
                f"Condition in 'do-while' must be bool-compatible, got '{cond_type}'."
            )

    # -----------------------------------------------------------------------
    # Expression type inference
    # -----------------------------------------------------------------------

    def _infer_type(self, node: ASTNode) -> str | None:
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

        # Array & built-in expressions
        if isinstance(node, ArrayLiteral):
            for elem in node.elements:
                self._infer_type(elem)
            return ARRAY
        if isinstance(node, IndexAccess):
            arr_type = self._infer_type(node.array)
            self._infer_type(node.index)
            if arr_type is not None and arr_type not in (ARRAY, ANY):
                self.errors.append(
                    f"Cannot index into type '{arr_type}'. Expected array."
                )
            return ANY
        if isinstance(node, RangeExpression):
            if node.start is not None:
                self._infer_type(node.start)
            self._infer_type(node.stop)
            if node.step is not None:
                self._infer_type(node.step)
            return ARRAY
        if isinstance(node, LenExpression):
            arg_type = self._infer_type(node.argument)
            if arg_type is not None and arg_type not in (ARRAY, ANY):
                self.errors.append(
                    f"'len()' requires an array, got '{arg_type}'."
                )
            return INT

        self.errors.append(f"Cannot infer type for node: {type(node).__name__}")
        return None

    def _infer_variable(self, node: Variable) -> str | None:
        if node.name in self.symbol_table:
            return self.symbol_table[node.name]
        self.errors.append(f"Undefined variable: '{node.name}'.")
        return None

    # -----------------------------------------------------------------------
    # Operator type rules
    # -----------------------------------------------------------------------

    def _check_binary_op(self, node: BinaryOp) -> str | None:
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)

        if left_type is None or right_type is None:
            return None

        # ANY is compatible with everything
        if left_type == ANY or right_type == ANY:
            return ANY

        # Guard against char operands
        if left_type == CHAR or right_type == CHAR:
            self.errors.append("Arithmetic on characters is not supported.")
            return None

        # Guard against bool operands
        if left_type == BOOL or right_type == BOOL:
            self.errors.append("Arithmetic on booleans is not supported.")
            return None

        # Both operands are int
        if left_type == INT and right_type == INT:
            if node.op == "/":
                return FLOAT
            return INT

        # Both operands are float
        if left_type == FLOAT and right_type == FLOAT:
            return FLOAT

        # Mixed int/float — promotion to float
        if {left_type, right_type} == {INT, FLOAT}:
            return FLOAT

        self.errors.append(
            f"Unsupported operand types for '{node.op}': "
            f"'{left_type}' and '{right_type}'."
        )
        return None

    def _check_unary_op(self, node: UnaryOp) -> str | None:
        operand_type = self._infer_type(node.operand)
        if operand_type is None:
            return None
        if operand_type == ANY:
            return ANY
        if operand_type in NUMERIC_TYPES:
            return operand_type
        self.errors.append(
            f"Unary '{node.op}' not supported for type '{operand_type}'."
        )
        return None

    def _check_comparison(self, node: Comparison) -> str | None:
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)

        if left_type is None or right_type is None:
            return None

        if left_type == ANY or right_type == ANY:
            return BOOL

        # Numeric comparisons
        if left_type in NUMERIC_TYPES and right_type in NUMERIC_TYPES:
            return BOOL

        # Char-to-char comparison
        if left_type == CHAR and right_type == CHAR:
            return BOOL

        # Bool-to-bool equality
        if left_type == BOOL and right_type == BOOL:
            if node.op in ("==", "!="):
                return BOOL
            self.errors.append(
                "Ordering comparisons on booleans are not supported."
            )
            return None

        self.errors.append(
            f"Cannot compare '{left_type}' with '{right_type}'."
        )
        return None

    def _check_boolean_op(self, node: BooleanOp) -> str | None:
        left_type = self._infer_type(node.left)
        right_type = self._infer_type(node.right)

        if left_type is None or right_type is None:
            return None

        if left_type == ANY or right_type == ANY:
            return BOOL

        bool_compatible = {BOOL, INT, FLOAT}
        if left_type in bool_compatible and right_type in bool_compatible:
            return BOOL

        self.errors.append(
            f"Operands of '{node.op}' must be bool-compatible, "
            f"got '{left_type}' and '{right_type}'."
        )
        return None

    def _check_not_op(self, node: NotOp) -> str | None:
        operand_type = self._infer_type(node.operand)
        if operand_type is None:
            return None
        if operand_type == ANY:
            return BOOL
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

    Returns the symbol table mapping variable names to type strings.
    Raises SemanticError if any semantic errors are detected.
    """
    analyzer = SemanticAnalyzer(symbol_table=symbol_table)
    analyzer.analyze(program)
    return analyzer.symbol_table
