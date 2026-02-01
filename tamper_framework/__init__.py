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

# Core transformations
from tamper_framework.transformations import (
    create_keyword_wrap_rule,
    create_space_replace_rule,
    create_case_alternate_rule,
    create_value_encode_rule,
)

# Advanced transformations (v2.1.0+)
from tamper_framework.transformations import (
    create_homoglyph_rule,
    create_function_wrap_rule,
    create_numeric_obfuscation_rule,
    create_comment_chaos_rule,
    create_logical_swap_rule,
    create_hex_encode_rule,
    create_version_comment_vary_rule,
)

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
    
    # Core Transformations
    'create_keyword_wrap_rule',
    'create_space_replace_rule',
    'create_case_alternate_rule',
    'create_value_encode_rule',
    
    # Advanced Transformations
    'create_homoglyph_rule',
    'create_function_wrap_rule',
    'create_numeric_obfuscation_rule',
    'create_comment_chaos_rule',
    'create_logical_swap_rule',
    'create_hex_encode_rule',
    'create_version_comment_vary_rule',
]
