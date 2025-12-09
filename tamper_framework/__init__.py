"""
SQL Tamper Framework

Context-aware SQL transformation framework with proper safeguards.

Author: Regaan
License: GPL v2
"""

from tamper_framework.__version__ import (
    __version__,
    __author__,
    __license__,
    __description__
)

from tamper_framework.lexer import SQLLexer, Token, TokenType
from tamper_framework.context import (
    SQLContext,
    SQLContextTracker,
    ClauseType,
    annotate_tokens_with_context
)
from tamper_framework.transformer import SQLTransformer, TransformationRule
from tamper_framework.ast_builder import (
    ASTNode,
    NodeType,
    SQLASTBuilder,
    reconstruct_from_ast
)
from tamper_framework.ast_transformer import ASTTransformer, ASTTransformationRule

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',
    '__description__',
    
    # Lexer
    'SQLLexer',
    'Token',
    'TokenType',
    
    # Context
    'SQLContext',
    'SQLContextTracker',
    'ClauseType',
    'annotate_tokens_with_context',
    
    # Transformer
    'SQLTransformer',
    'TransformationRule',
    
    # AST
    'ASTNode',
    'NodeType',
    'SQLASTBuilder',
    'reconstruct_from_ast',
    'ASTTransformer',
    'ASTTransformationRule',
]
