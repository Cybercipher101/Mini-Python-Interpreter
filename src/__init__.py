# Mini Python Interpreter - Source Package
# This package contains the modular components of the interpreter:
#   - grammar:           Lark grammar specification
#   - lexer_parser:      Frontend (tokenization + AST construction)
#   - ast_nodes:         AST node dataclass definitions
#   - semantic_analyzer: Middleware (symbol table + type checker)
#   - evaluator:         Backend (AST traversal via Visitor Pattern)
#   - cli:               Command-line interface

__version__ = "1.0.0"
