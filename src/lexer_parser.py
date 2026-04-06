"""
lexer_parser.py — Frontend: Lexer & Parser
============================================

Responsibilities:
  1. Feed the source text to Lark, which performs *lexing* (tokenisation) and
     *parsing* (syntax analysis) in one step.
  2. Transform the resulting Lark ``Tree`` into our own typed AST (see
     ``ast_nodes.py``) using a Lark ``Transformer``.

Public API:
  • ``parse(source: str) -> Program``  — the single entry-point used by
    downstream modules.
  • ``tokenize(source: str) -> list[dict]``  — extract raw tokens for the
    visualizer frontend.

Design Notes:
  • Lark's ``IndentTransformer`` is used as a post-lexer to generate
    INDENT / DEDENT tokens, mirroring Python's own indentation-sensitivity.
  • The ``ASTBuilder`` transformer converts every grammar rule into the
    corresponding ``ASTNode`` subclass.
"""

from __future__ import annotations

from typing import Any

from lark import Lark, Token, Transformer, v_args
from lark.indenter import Indenter

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
from src.grammar import MINI_PYTHON_GRAMMAR


# ---------------------------------------------------------------------------
# Indentation handler
# ---------------------------------------------------------------------------

class MiniPythonIndenter(Indenter):
    """Generates INDENT / DEDENT tokens for Lark's parser."""
    NL_type: str = "_NL"
    OPEN_PAREN_types: list[str] = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types: list[str] = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type: str = "_INDENT"
    DEDENT_type: str = "_DEDENT"
    tab_len: int = 4


# ---------------------------------------------------------------------------
# AST Builder Transformer
# ---------------------------------------------------------------------------

@v_args(inline=True)
class ASTBuilder(Transformer):
    """
    Walks the Lark parse-tree and constructs our typed AST.

    Each method name matches a grammar rule or alias.  Lark calls these
    methods bottom-up, so child nodes are already transformed when a
    parent method executes.
    """

    # --- Literals --------------------------------------------------------

    def int_literal(self, token: Token) -> IntLiteral:
        """Convert an INT token to an IntLiteral node."""
        return IntLiteral(value=int(token))

    def float_literal(self, token: Token) -> FloatLiteral:
        """Convert a FLOAT token to a FloatLiteral node."""
        return FloatLiteral(value=float(token))

    def char_literal(self, token: Token) -> CharLiteral:
        """
        Convert a CHAR token (e.g. ``'a'``) to a CharLiteral node.

        The surrounding single-quotes are stripped so that only the
        character itself is stored.
        """
        # Lark gives us the raw matched text including the quotes.
        raw: str = str(token)
        return CharLiteral(value=raw[1:-1])

    def true_literal(self) -> BoolLiteral:
        return BoolLiteral(value=True)

    def false_literal(self) -> BoolLiteral:
        return BoolLiteral(value=False)

    # --- Variable reference ----------------------------------------------

    def variable(self, name: Token) -> Variable:
        return Variable(name=str(name))

    # --- Arithmetic operators --------------------------------------------

    def add(self, left: ASTNode, right: ASTNode) -> BinaryOp:
        return BinaryOp(op="+", left=left, right=right)

    def sub(self, left: ASTNode, right: ASTNode) -> BinaryOp:
        return BinaryOp(op="-", left=left, right=right)

    def mul(self, left: ASTNode, right: ASTNode) -> BinaryOp:
        return BinaryOp(op="*", left=left, right=right)

    def div(self, left: ASTNode, right: ASTNode) -> BinaryOp:
        return BinaryOp(op="/", left=left, right=right)

    def floor_div(self, left: ASTNode, right: ASTNode) -> BinaryOp:
        return BinaryOp(op="//", left=left, right=right)

    def mod(self, left: ASTNode, right: ASTNode) -> BinaryOp:
        return BinaryOp(op="%", left=left, right=right)

    def power(self, base: ASTNode, exp: ASTNode) -> BinaryOp:
        return BinaryOp(op="**", left=base, right=exp)

    # --- Unary operators -------------------------------------------------

    def unary_pos(self, operand: ASTNode) -> UnaryOp:
        return UnaryOp(op="+", operand=operand)

    def unary_neg(self, operand: ASTNode) -> UnaryOp:
        return UnaryOp(op="-", operand=operand)

    # --- Comparison & boolean operators ----------------------------------

    def compare(self, left: ASTNode, op: Token, right: ASTNode) -> Comparison:
        return Comparison(op=str(op), left=left, right=right)

    def and_op(self, left: ASTNode, right: ASTNode) -> BooleanOp:
        return BooleanOp(op="and", left=left, right=right)

    def or_op(self, left: ASTNode, right: ASTNode) -> BooleanOp:
        return BooleanOp(op="or", left=left, right=right)

    def not_op(self, operand: ASTNode) -> NotOp:
        return NotOp(operand=operand)

    # --- Statements ------------------------------------------------------

    def assignment(self, name: Token, value: ASTNode) -> Assignment:
        return Assignment(name=str(name), value=value)

    def index_assignment(self, name: Token, index: ASTNode, value: ASTNode) -> IndexAssignment:
        return IndexAssignment(name=str(name), index=index, value=value)

    def print_statement(self, expression: ASTNode) -> PrintStatement:
        return PrintStatement(expression=expression)

    # --- If / Elif / Else ------------------------------------------------

    def block(self, *statements: ASTNode) -> tuple[ASTNode, ...]:
        """A block is just a sequence of statements; return as a tuple."""
        return tuple(statements)

    def elif_clause(self, condition: ASTNode, body: tuple) -> ElifClause:
        return ElifClause(condition=condition, body=body)

    def else_clause(self, body: tuple) -> ElseClause:
        return ElseClause(body=body)

    def if_statement(self, *args: Any) -> IfStatement:
        """
        Build an IfStatement from the variable-length children:
            condition, body, *elif_clauses, [else_clause]
        """
        condition: ASTNode = args[0]
        body: tuple[ASTNode, ...] = args[1]

        elif_clauses: list[ElifClause] = []
        else_clause: ElseClause | None = None

        for child in args[2:]:
            if isinstance(child, ElifClause):
                elif_clauses.append(child)
            elif isinstance(child, ElseClause):
                else_clause = child

        return IfStatement(
            condition=condition,
            body=body,
            elif_clauses=tuple(elif_clauses),
            else_clause=else_clause,
        )

    # --- Loops -----------------------------------------------------------

    def while_statement(self, condition: ASTNode, body: tuple) -> WhileStatement:
        return WhileStatement(condition=condition, body=body)

    def for_statement(self, name: Token, iterable: ASTNode, body: tuple) -> ForStatement:
        return ForStatement(variable=str(name), iterable=iterable, body=body)

    def do_while_statement(self, body: tuple, condition: ASTNode) -> DoWhileStatement:
        return DoWhileStatement(condition=condition, body=body)

    # --- Arrays ----------------------------------------------------------

    def empty_array(self) -> ArrayLiteral:
        return ArrayLiteral(elements=())

    def array_literal(self, *elements: ASTNode) -> ArrayLiteral:
        return ArrayLiteral(elements=tuple(elements))

    def index_access(self, array: ASTNode, index: ASTNode) -> IndexAccess:
        return IndexAccess(array=array, index=index)

    # --- Built-in expressions --------------------------------------------

    def range_expr(self, *args: ASTNode) -> RangeExpression:
        if len(args) == 1:
            return RangeExpression(start=None, stop=args[0], step=None)
        elif len(args) == 2:
            return RangeExpression(start=args[0], stop=args[1], step=None)
        else:
            return RangeExpression(start=args[0], stop=args[1], step=args[2])

    def len_expr(self, argument: ASTNode) -> LenExpression:
        return LenExpression(argument=argument)

    # --- Program (root) --------------------------------------------------

    def program(self, *statements: ASTNode) -> Program:
        return Program(statements=tuple(statements))


# ---------------------------------------------------------------------------
# Parser singleton & public API
# ---------------------------------------------------------------------------

_parser: Lark | None = None


def _get_parser() -> Lark:
    """Lazily create and cache the Lark parser."""
    global _parser
    if _parser is None:
        _parser = Lark(
            MINI_PYTHON_GRAMMAR,
            parser="lalr",
            postlex=MiniPythonIndenter(),
            start="program",
            propagate_positions=True,   # attach line/col info for errors
        )
    return _parser


def parse(source: str) -> Program:
    """
    Parse a mini-Python source string and return the AST root.

    Parameters
    ----------
    source : str
        Complete mini-Python program text.

    Returns
    -------
    Program
        The root AST node containing all top-level statements.

    Raises
    ------
    lark.exceptions.UnexpectedInput
        On syntax errors (unexpected token or character).
    """
    tree = _get_parser().parse(source + "\n")  # ensure trailing newline
    ast: Program = ASTBuilder().transform(tree)
    return ast


def tokenize(source: str) -> list[dict]:
    """
    Tokenize source code and return a list of token dicts for the visualizer.

    Each dict has keys: type, lexeme, line.
    Returns as many tokens as possible; does not raise on errors.
    """
    tokens = []
    try:
        parser = _get_parser()
        lexer_tokens = parser.lex(source + "\n")
        for tok in lexer_tokens:
            tok_type = str(tok.type)
            # Skip internal whitespace/newline tokens
            if tok_type.startswith("_") or tok_type == "WS_INLINE":
                continue
            tokens.append({
                "type": tok_type,
                "lexeme": str(tok),
                "line": getattr(tok, "line", 0),
            })
    except Exception:
        pass  # Return whatever tokens we managed to extract
    return tokens
