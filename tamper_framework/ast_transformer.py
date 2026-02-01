#!/usr/bin/env python

"""
AST-Based Transformer

Transforms SQL using AST structure for better accuracy.

Author: Regaan
License: GPL v2
"""

from typing import List, Callable
from tamper_framework.lexer import Token, TokenType, SQLLexer
from tamper_framework.ast_builder import ASTNode, NodeType, SQLASTBuilder, reconstruct_from_ast
from tamper_framework.context import SQLContext, ClauseType


class ASTTransformationRule:
    """
    AST-aware transformation rule
    
    Can transform based on:
    - Node type (SELECT, SUBQUERY, FUNCTION, etc.)
    - Node depth (nesting level)
    - Parent node type
    """
    
    def __init__(
        self,
        name: str,
        transform_func: Callable[[Token, ASTNode], Token],
        target_token_types: List[TokenType],
        target_node_types: List[NodeType] = None,
        max_depth: int = None
    ):
        self.name = name
        self.transform_func = transform_func
        self.target_token_types = target_token_types
        self.target_node_types = target_node_types  # If set, only transform in these node types
        self.max_depth = max_depth  # If set, only transform up to this depth
    
    def should_transform(self, token: Token, node: ASTNode) -> bool:
        """Check if token should be transformed"""
        # Check token type
        if token.type not in self.target_token_types:
            return False
        
        # Check node type if specified
        if self.target_node_types and node.type not in self.target_node_types:
            return False
        
        # Check depth if specified
        if self.max_depth is not None and node.get_depth() > self.max_depth:
            return False
        
        return True
    
    def apply(self, token: Token, node: ASTNode) -> Token:
        """Apply transformation"""
        if not self.should_transform(token, node):
            return token
        
        return self.transform_func(token, node)


class ASTTransformer:
    """
    AST-based SQL transformer
    
    Advantages over token-based:
    - Knows nesting structure
    - Can transform based on parent/child relationships
    - Better handling of subqueries
    """
    
    def __init__(self):
        self.rules: List[ASTTransformationRule] = []
    
    def add_rule(self, rule: ASTTransformationRule):
        """Add transformation rule"""
        self.rules.append(rule)
    
    def transform(self, sql: str) -> str:
        """Transform SQL using AST"""
        # Tokenize
        lexer = SQLLexer(sql)
        tokens = lexer.tokenize()
        
        # Build AST
        builder = SQLASTBuilder(tokens)
        ast = builder.build()
        
        # Transform AST
        self._transform_node(ast)
        
        # Reconstruct
        return reconstruct_from_ast(ast)
    
    def _transform_node(self, node: ASTNode):
        """Recursively transform a node and its children"""
        # Transform tokens in this node
        transformed_tokens = []
        for token in node.tokens:
            new_token = token
            for rule in self.rules:
                new_token = rule.apply(new_token, node)
            transformed_tokens.append(new_token)
        
        node.tokens = transformed_tokens
        
        # Transform children
        for child in node.children:
            self._transform_node(child)


if __name__ == "__main__":
    # Test AST-based transformation
    
    def wrap_keyword_in_select(token: Token, node: ASTNode) -> Token:
        """Wrap keywords, but only in top-level SELECT (not subqueries)"""
        if token.type == TokenType.KEYWORD and node.get_depth() == 1:
            new_value = f'/*!50000{token.value}*/'
            return Token(
                id=token.id,
                type=token.type,
                value=new_value,
                position=token.position,
                line=token.line,
                column=token.column
            )
        return token
    
    # Create rule that only transforms in top-level SELECT
    rule = ASTTransformationRule(
        name="top_level_keyword_wrap",
        transform_func=wrap_keyword_in_select,
        target_token_types=[TokenType.KEYWORD],
        target_node_types=[NodeType.SELECT_STATEMENT],
        max_depth=1  # Only top level
    )
    
    # Test
    transformer = ASTTransformer()
    transformer.add_rule(rule)
    
    queries = [
        "SELECT * FROM users WHERE id=1",
        "SELECT * FROM (SELECT id FROM users) WHERE id>5"
    ]
    
    print("AST-Based Transformation Test")
    print("=" * 70)
    
    for query in queries:
        result = transformer.transform(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
        print("Notice: Only top-level SELECT keywords are wrapped")
        print("        Subquery keywords are NOT wrapped (depth > 1)")
