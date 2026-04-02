"""
test_interpreter.py — Comprehensive Test Suite
================================================

This test suite covers all three pipeline stages:
  • Frontend  (Lexer/Parser)   — tests that source code produces correct ASTs
  • Middleware (Semantic Analyzer) — tests that type errors are caught
  • Backend   (Evaluator)      — tests that execution produces correct output

Test Organization
-----------------
Tests are grouped into classes by feature area for clarity:
  • TestLexerParser         — parsing and AST construction
  • TestSemanticAnalyzer    — type-checking and symbol table
  • TestEvaluator           — runtime execution
  • TestIntegration         — end-to-end pipeline tests
  • TestEdgeCases           — boundary conditions and tricky inputs

How to Add Your Own Tests
--------------------------
1. Choose the appropriate class based on which layer you are testing.
2. Write a function starting with ``test_``.
3. For parser tests:
   - Call ``parse(source)`` and assert on the returned AST structure.
   - Example: ``assert isinstance(ast.statements[0], Assignment)``
4. For semantic tests:
   - Call ``parse(source)`` then ``analyze(ast)``.
   - Use ``pytest.raises(SemanticError)`` for error cases.
5. For evaluator tests:
   - Use the helper ``_run(source)`` to get ``(output, variables)``.
   - Assert on printed output and/or variable values.
6. Mark tests for unimplemented TODOs with ``@pytest.mark.xfail``
   so they are expected to fail until you implement the feature.

Running the Tests
-----------------
    cd "Mini Python Interpreter"
    pytest tests/ -v
    pytest tests/ -v --tb=short   # shorter tracebacks
    pytest tests/ -v -k "test_add" # run only tests matching a pattern
"""

from __future__ import annotations

import pytest

from src.ast_nodes import (
    Assignment,
    BinaryOp,
    BoolLiteral,
    CharLiteral,
    Comparison,
    FloatLiteral,
    IfStatement,
    IntLiteral,
    PrintStatement,
    Program,
    UnaryOp,
    Variable,
)
from src.evaluator import EvalError, Evaluator, evaluate
from src.lexer_parser import parse
from src.semantic_analyzer import SemanticError, analyze


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _run(source: str) -> tuple[str, dict]:
    """Parse → Analyze → Evaluate.  Returns (output, variables)."""
    ast = parse(source)
    analyze(ast)
    return evaluate(ast)


# ===========================================================================
# FRONTEND TESTS — Lexer / Parser
# ===========================================================================

class TestLexerParser:
    """Tests that source code is correctly parsed into AST nodes."""

    def test_parse_int_literal(self) -> None:
        """Parsing a bare integer should produce an IntLiteral in a print."""
        ast = parse("print(42)")
        assert isinstance(ast, Program)
        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expression, IntLiteral)
        assert stmt.expression.value == 42

    def test_parse_float_literal(self) -> None:
        ast = parse("print(3.14)")
        stmt = ast.statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expression, FloatLiteral)
        assert stmt.expression.value == pytest.approx(3.14)

    def test_parse_char_literal(self) -> None:
        ast = parse("print('a')")
        stmt = ast.statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expression, CharLiteral)
        assert stmt.expression.value == "a"

    def test_parse_bool_true(self) -> None:
        ast = parse("print(True)")
        stmt = ast.statements[0]
        assert isinstance(stmt, PrintStatement)
        assert isinstance(stmt.expression, BoolLiteral)
        assert stmt.expression.value is True

    def test_parse_bool_false(self) -> None:
        ast = parse("print(False)")
        stmt = ast.statements[0]
        assert isinstance(stmt.expression, BoolLiteral)
        assert stmt.expression.value is False

    def test_parse_assignment(self) -> None:
        ast = parse("x = 10")
        stmt = ast.statements[0]
        assert isinstance(stmt, Assignment)
        assert stmt.name == "x"
        assert isinstance(stmt.value, IntLiteral)
        assert stmt.value.value == 10

    def test_parse_binary_add(self) -> None:
        ast = parse("print(1 + 2)")
        expr = ast.statements[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"

    def test_parse_operator_precedence(self) -> None:
        """``1 + 2 * 3`` should parse as ``1 + (2 * 3)``."""
        ast = parse("print(1 + 2 * 3)")
        expr = ast.statements[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.op == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == "*"

    def test_parse_parenthesised_expression(self) -> None:
        """``(1 + 2) * 3`` should parse as ``(1 + 2) * 3``."""
        ast = parse("print((1 + 2) * 3)")
        expr = ast.statements[0].expression
        assert isinstance(expr, BinaryOp)
        assert expr.op == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == "+"

    def test_parse_unary_neg(self) -> None:
        ast = parse("print(-5)")
        expr = ast.statements[0].expression
        assert isinstance(expr, UnaryOp)
        assert expr.op == "-"

    def test_parse_comparison(self) -> None:
        ast = parse("print(1 == 2)")
        expr = ast.statements[0].expression
        assert isinstance(expr, Comparison)
        assert expr.op == "=="

    def test_parse_if_statement(self) -> None:
        source = """\
if True:
    print(1)
"""
        ast = parse(source)
        stmt = ast.statements[0]
        assert isinstance(stmt, IfStatement)
        assert isinstance(stmt.condition, BoolLiteral)
        assert len(stmt.body) == 1

    def test_parse_if_else(self) -> None:
        source = """\
if False:
    print(1)
else:
    print(2)
"""
        ast = parse(source)
        stmt = ast.statements[0]
        assert isinstance(stmt, IfStatement)
        assert stmt.else_clause is not None

    def test_parse_multiple_statements(self) -> None:
        source = """\
x = 1
y = 2
print(x)
"""
        ast = parse(source)
        assert len(ast.statements) == 3

    def test_syntax_error_raises(self) -> None:
        """Malformed input should raise a Lark exception."""
        with pytest.raises(Exception):  # UnexpectedInput or similar
            parse("print(")


# ===========================================================================
# MIDDLEWARE TESTS — Semantic Analyzer
# ===========================================================================

class TestSemanticAnalyzer:
    """Tests for type checking and symbol table construction."""

    def test_int_variable_type(self) -> None:
        ast = parse("x = 42")
        symbols = analyze(ast)
        assert symbols["x"] == "int"

    def test_float_variable_type(self) -> None:
        ast = parse("x = 3.14")
        symbols = analyze(ast)
        assert symbols["x"] == "float"

    def test_char_variable_type(self) -> None:
        ast = parse("x = 'a'")
        symbols = analyze(ast)
        assert symbols["x"] == "char"

    def test_bool_variable_type(self) -> None:
        ast = parse("x = True")
        symbols = analyze(ast)
        assert symbols["x"] == "bool"

    def test_int_plus_int_is_int(self) -> None:
        ast = parse("x = 1 + 2")
        symbols = analyze(ast)
        assert symbols["x"] == "int"

    def test_int_plus_float_is_float(self) -> None:
        ast = parse("x = 1 + 2.5")
        symbols = analyze(ast)
        assert symbols["x"] == "float"

    def test_true_division_is_float(self) -> None:
        """``int / int`` always yields float in the type system."""
        ast = parse("x = 10 / 3")
        symbols = analyze(ast)
        assert symbols["x"] == "float"

    def test_undefined_variable_error(self) -> None:
        ast = parse("print(z)")
        with pytest.raises(SemanticError, match="Undefined variable"):
            analyze(ast)

    def test_type_mismatch_reassignment(self) -> None:
        source = """\
x = 42
x = 'a'
"""
        ast = parse(source)
        with pytest.raises(SemanticError, match="Type mismatch"):
            analyze(ast)

    def test_int_to_float_promotion_on_reassignment(self) -> None:
        """Reassigning a float to an int variable promotes the type."""
        source = """\
x = 10
x = 3.14
"""
        ast = parse(source)
        symbols = analyze(ast)
        assert symbols["x"] == "float"

    def test_comparison_yields_bool(self) -> None:
        ast = parse("x = 1 == 2")
        symbols = analyze(ast)
        assert symbols["x"] == "bool"

    def test_unary_on_char_error(self) -> None:
        ast = parse("x = -'a'")
        with pytest.raises(SemanticError, match="not supported"):
            analyze(ast)

    # ── Tests for TODO exercises ──────────────────────────────────────
    # These tests are marked xfail because the corresponding type-check
    # rules are left as TODOs for students.  Once you implement them,
    # remove the xfail decorator and they should pass.

    def test_char_arithmetic_error(self) -> None:
        """Arithmetic on char operands should be a semantic error."""
        ast = parse("x = 'a' + 'b'")
        with pytest.raises(SemanticError):
            analyze(ast)

    def test_bool_arithmetic_error(self) -> None:
        """Arithmetic on bool operands should be a semantic error."""
        ast = parse("x = True + False")
        with pytest.raises(SemanticError):
            analyze(ast)

    @pytest.mark.xfail(reason="TODO: Bool-to-bool comparison for == and !=")
    def test_bool_equality_comparison(self) -> None:
        """``bool == bool`` should be valid and yield bool."""
        ast = parse("x = True == False")
        symbols = analyze(ast)
        assert symbols["x"] == "bool"


# ===========================================================================
# BACKEND TESTS — Evaluator
# ===========================================================================

class TestEvaluator:
    """Tests for the runtime execution engine."""

    def test_print_int(self) -> None:
        output, _ = _run("print(42)")
        assert output.strip() == "42"

    def test_print_float(self) -> None:
        output, _ = _run("print(3.14)")
        assert output.strip() == "3.14"

    def test_print_char(self) -> None:
        output, _ = _run("print('z')")
        assert output.strip() == "z"

    def test_print_bool(self) -> None:
        output, _ = _run("print(True)")
        assert output.strip() == "True"

    def test_addition(self) -> None:
        output, _ = _run("print(3 + 4)")
        assert output.strip() == "7"

    def test_subtraction(self) -> None:
        output, _ = _run("print(10 - 3)")
        assert output.strip() == "7"

    def test_multiplication(self) -> None:
        output, _ = _run("print(6 * 7)")
        assert output.strip() == "42"

    def test_true_division(self) -> None:
        output, _ = _run("print(7 / 2)")
        assert output.strip() == "3.5"

    def test_division_by_zero(self) -> None:
        with pytest.raises(EvalError, match="Division by zero"):
            _run("print(1 / 0)")

    def test_unary_negative(self) -> None:
        output, _ = _run("print(-5)")
        assert output.strip() == "-5"

    def test_unary_positive(self) -> None:
        output, _ = _run("print(+3)")
        assert output.strip() == "3"

    def test_variable_assignment_and_retrieval(self) -> None:
        output, variables = _run("x = 42\nprint(x)")
        assert output.strip() == "42"
        assert variables["x"] == 42

    def test_variable_reassignment(self) -> None:
        output, variables = _run("x = 1\nx = 2\nprint(x)")
        assert output.strip() == "2"
        assert variables["x"] == 2

    def test_complex_expression(self) -> None:
        """``(2 + 3) * 4 - 1`` should be ``19``."""
        output, _ = _run("print((2 + 3) * 4 - 1)")
        assert output.strip() == "19"

    def test_nested_arithmetic(self) -> None:
        output, _ = _run("print(2 * (3 + 4 * (5 - 2)))")
        # 5-2=3, 4*3=12, 3+12=15, 2*15=30
        assert output.strip() == "30"

    def test_comparison_equal_true(self) -> None:
        output, _ = _run("print(5 == 5)")
        assert output.strip() == "True"

    def test_comparison_equal_false(self) -> None:
        output, _ = _run("print(5 == 3)")
        assert output.strip() == "False"

    def test_comparison_not_equal(self) -> None:
        output, _ = _run("print(5 != 3)")
        assert output.strip() == "True"

    def test_not_operator(self) -> None:
        output, _ = _run("print(not True)")
        assert output.strip() == "False"

    def test_not_on_zero(self) -> None:
        output, _ = _run("print(not 0)")
        assert output.strip() == "True"

    def test_mixed_int_float_arithmetic(self) -> None:
        output, _ = _run("print(1 + 2.5)")
        assert output.strip() == "3.5"

    def test_if_true_branch(self) -> None:
        source = """\
if True:
    print(1)
"""
        output, _ = _run(source)
        assert output.strip() == "1"

    def test_if_false_no_output(self) -> None:
        source = """\
if False:
    print(1)
"""
        output, _ = _run(source)
        assert output.strip() == ""

    def test_multiple_prints(self) -> None:
        source = """\
print(1)
print(2)
print(3)
"""
        output, _ = _run(source)
        lines = output.strip().split("\n")
        assert lines == ["1", "2", "3"]

    def test_variable_in_expression(self) -> None:
        source = """\
x = 10
y = 20
print(x + y)
"""
        output, _ = _run(source)
        assert output.strip() == "30"

    # ── Tests for TODO exercises ──────────────────────────────────────
    # These tests verify features left as TODOs in the evaluator.
    # They are marked xfail until you implement the corresponding code.

    @pytest.mark.xfail(reason="TODO: Floor division operator //")
    def test_floor_division(self) -> None:
        output, _ = _run("print(7 // 2)")
        assert output.strip() == "3"

    @pytest.mark.xfail(reason="TODO: Modulo operator %")
    def test_modulo(self) -> None:
        output, _ = _run("print(10 % 3)")
        assert output.strip() == "1"

    @pytest.mark.xfail(reason="TODO: Exponentiation operator **")
    def test_exponentiation(self) -> None:
        output, _ = _run("print(2 ** 10)")
        assert output.strip() == "1024"

    @pytest.mark.xfail(reason="TODO: Less than operator <")
    def test_less_than(self) -> None:
        output, _ = _run("print(3 < 5)")
        assert output.strip() == "True"

    @pytest.mark.xfail(reason="TODO: Greater than operator >")
    def test_greater_than(self) -> None:
        output, _ = _run("print(5 > 3)")
        assert output.strip() == "True"

    @pytest.mark.xfail(reason="TODO: Less than or equal <=")
    def test_less_equal(self) -> None:
        output, _ = _run("print(3 <= 3)")
        assert output.strip() == "True"

    @pytest.mark.xfail(reason="TODO: Greater than or equal >=")
    def test_greater_equal(self) -> None:
        output, _ = _run("print(5 >= 5)")
        assert output.strip() == "True"

    @pytest.mark.xfail(reason="TODO: Boolean 'and' operator")
    def test_and_operator(self) -> None:
        output, _ = _run("print(True and False)")
        assert output.strip() == "False"

    @pytest.mark.xfail(reason="TODO: Boolean 'or' operator")
    def test_or_operator(self) -> None:
        output, _ = _run("print(False or True)")
        assert output.strip() == "True"

    @pytest.mark.xfail(reason="TODO: elif clause evaluation")
    def test_if_elif(self) -> None:
        source = """\
x = 2
if x == 1:
    print(10)
elif x == 2:
    print(20)
"""
        output, _ = _run(source)
        assert output.strip() == "20"

    @pytest.mark.xfail(reason="TODO: else clause evaluation")
    def test_if_else(self) -> None:
        source = """\
if False:
    print(1)
else:
    print(2)
"""
        output, _ = _run(source)
        assert output.strip() == "2"

    @pytest.mark.xfail(reason="TODO: Floor division by zero")
    def test_floor_division_by_zero(self) -> None:
        with pytest.raises(EvalError, match="Division by zero"):
            _run("print(5 // 0)")

    @pytest.mark.xfail(reason="TODO: Modulo by zero")
    def test_modulo_by_zero(self) -> None:
        with pytest.raises(EvalError, match="Modulo by zero"):
            _run("print(5 % 0)")

    @pytest.mark.xfail(reason="TODO: Short-circuit and")
    def test_and_short_circuit(self) -> None:
        """``False and <anything>`` should not evaluate the RHS."""
        output, _ = _run("print(False and True)")
        assert output.strip() == "False"

    @pytest.mark.xfail(reason="TODO: Short-circuit or")
    def test_or_short_circuit(self) -> None:
        """``True or <anything>`` should not evaluate the RHS."""
        output, _ = _run("print(True or False)")
        assert output.strip() == "True"


# ===========================================================================
# INTEGRATION TESTS — Full pipeline
# ===========================================================================

class TestIntegration:
    """End-to-end tests that exercise the full pipeline."""

    def test_temperature_conversion(self) -> None:
        """A small program that converts Celsius to Fahrenheit."""
        source = """\
celsius = 100
fahrenheit = celsius * 9 / 5 + 32
print(fahrenheit)
"""
        output, variables = _run(source)
        assert float(output.strip()) == pytest.approx(212.0)
        assert variables["celsius"] == 100

    def test_variable_swap_via_temp(self) -> None:
        source = """\
a = 1
b = 2
temp = a
a = b
b = temp
print(a)
print(b)
"""
        output, variables = _run(source)
        lines = output.strip().split("\n")
        assert lines == ["2", "1"]
        assert variables["a"] == 2
        assert variables["b"] == 1

    def test_comparison_chain_with_if(self) -> None:
        source = """\
x = 10
if x == 10:
    print(99)
"""
        output, _ = _run(source)
        assert output.strip() == "99"

    def test_multiple_variable_expressions(self) -> None:
        source = """\
a = 5
b = 3
c = a * b + 2
print(c)
"""
        output, variables = _run(source)
        assert output.strip() == "17"
        assert variables["c"] == 17


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================

class TestEdgeCases:
    """Boundary conditions and corner cases."""

    def test_large_integer(self) -> None:
        output, _ = _run("print(999999999999)")
        assert output.strip() == "999999999999"

    def test_negative_float(self) -> None:
        output, _ = _run("print(-0.5)")
        assert output.strip() == "-0.5"

    def test_deeply_nested_parens(self) -> None:
        output, _ = _run("print(((((42)))))")
        assert output.strip() == "42"

    def test_zero_operations(self) -> None:
        output, _ = _run("print(0 + 0)")
        assert output.strip() == "0"

    def test_negative_result(self) -> None:
        output, _ = _run("print(3 - 10)")
        assert output.strip() == "-7"

    def test_float_precision(self) -> None:
        output, _ = _run("print(0.1 + 0.2)")
        # Python float arithmetic: 0.1 + 0.2 = 0.30000000000000004
        result = float(output.strip())
        assert result == pytest.approx(0.3, abs=1e-10)

    def test_reassign_same_value(self) -> None:
        source = """\
x = 5
x = 5
print(x)
"""
        output, _ = _run(source)
        assert output.strip() == "5"

    def test_char_comparison_equal(self) -> None:
        output, _ = _run("print('a' == 'a')")
        assert output.strip() == "True"

    def test_char_comparison_not_equal(self) -> None:
        output, _ = _run("print('a' != 'b')")
        assert output.strip() == "True"

    def test_empty_program(self) -> None:
        """An empty source should produce no output."""
        output, _ = _run("")
        assert output == ""

    def test_whitespace_only_program(self) -> None:
        output, _ = _run("   \n\n   \n")
        assert output == ""
