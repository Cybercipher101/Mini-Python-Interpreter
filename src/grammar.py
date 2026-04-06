"""
grammar.py — Lark Grammar Specification for the Mini-Python Interpreter
========================================================================

This module defines the EBNF-style grammar consumed by Lark's LALR parser.
The grammar covers all language features within scope:

  • Integer and float literals
  • Character literals (single-quoted, one character)
  • Arithmetic expressions with correct precedence (+, -, *, /, //, %, **)
  • Variable assignment (single global scope)
  • Conditional statements (if / elif / else)
  • Comparison and boolean operators
  • A built-in ``print`` statement for output
  • While, for, and do-while loops
  • Array literals, indexing, and index assignment
  • Built-in ``range()`` and ``len()`` expressions

Design Notes
------------
* Operator precedence is encoded structurally (lower rules = lower precedence).
* ``print`` is treated as a *statement*, not a function call.
* Loops support while, for-in, and do-while constructs.
* Arrays are first-class values supporting indexing and assignment.
"""

# ---------------------------------------------------------------------------
# Lark Grammar  (LALR-compatible)
# ---------------------------------------------------------------------------

MINI_PYTHON_GRAMMAR: str = r"""
    // ===================================================================
    // Top-Level Program
    // ===================================================================
    // A program is one or more statements separated by newlines.
    program: (_NL* statement)*  _NL*

    // ===================================================================
    // Statements
    // ===================================================================
    ?statement: assignment
              | index_assignment
              | if_statement
              | while_statement
              | for_statement
              | do_while_statement
              | print_statement

    // Variable assignment:  <name> = <expression>
    assignment: NAME "=" expression

    // Array index assignment:  <name>[<index>] = <expression>
    index_assignment: NAME "[" expression "]" "=" expression

    // Print statement:  print(<expression>)
    print_statement: "print" "(" expression ")"

    // If / elif / else block
    if_statement: "if" expression ":" block \
                  elif_clause* \
                  else_clause?

    elif_clause: "elif" expression ":" block
    else_clause: "else" ":" block

    // While loop:  while <condition>: <block>
    while_statement: "while" expression ":" block

    // For loop:  for <name> in <expression>: <block>
    for_statement: "for" NAME "in" expression ":" block

    // Do-while loop:  do: <block> while <expression>
    do_while_statement: "do" ":" block "while" expression

    // A block is one or more indented statements.
    block: _NL _INDENT (statement _NL)+ _DEDENT

    // ===================================================================
    // Expressions  (precedence: low → high, top → bottom)
    // ===================================================================
    ?expression: or_expr

    ?or_expr: and_expr
            | or_expr "or" and_expr          -> or_op

    ?and_expr: not_expr
             | and_expr "and" not_expr       -> and_op

    ?not_expr: comparison
             | "not" not_expr                -> not_op

    ?comparison: arith_expr
               | comparison COMP_OP arith_expr  -> compare

    COMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

    // Arithmetic ---------------------------------------------------------
    ?arith_expr: term
               | arith_expr "+" term         -> add
               | arith_expr "-" term         -> sub

    ?term: factor
         | term "*" factor                   -> mul
         | term "/" factor                   -> div
         | term "//" factor                  -> floor_div
         | term "%" factor                   -> mod

    ?factor: power
           | "+" factor                      -> unary_pos
           | "-" factor                      -> unary_neg

    ?power: postfix
          | postfix "**" factor              -> power

    // Postfix (indexing) --------------------------------------------------
    ?postfix: atom
            | postfix "[" expression "]"     -> index_access

    // Atoms (highest precedence) -----------------------------------------
    ?atom: INT                               -> int_literal
         | FLOAT                             -> float_literal
         | CHAR                              -> char_literal
         | "True"                            -> true_literal
         | "False"                           -> false_literal
         | NAME                              -> variable
         | "(" expression ")"
         | "[" "]"                           -> empty_array
         | "[" expression ("," expression)* "]"  -> array_literal
         | "range" "(" expression ("," expression)* ")"  -> range_expr
         | "len" "(" expression ")"          -> len_expr

    // ===================================================================
    // Terminals
    // ===================================================================
    // Character literal: a single character enclosed in single quotes.
    CHAR: "'" /[^'\\]/ "'"

    // Use Lark's built-in terminals for INT, FLOAT, NAME.
    // FLOAT must appear before INT so '3.14' is not tokenised as INT+DOT+INT.

    // ===================================================================
    // Whitespace & Newlines
    // ===================================================================
    %import common.INT
    %import common.FLOAT
    %import common.CNAME -> NAME
    %import common.WS_INLINE
    %declare _INDENT _DEDENT

    _NL: /(\r?\n[\t ]*)+/

    // Ignore inline whitespace (spaces & tabs within a line)
    %ignore WS_INLINE
    %ignore /\\[\t ]*\r?\n/   // line continuation
"""
