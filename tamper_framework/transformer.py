#!/usr/bin/env python

"""
SQL Transformer - Context-aware token transformation

Uses UUID tracking and SQL context for safe transformations.

Author: Regaan
License: GPL v2
"""

from typing import List, Callable, Dict, Any, Set
from tamper_framework.lexer import Token, TokenType, SQLLexer
from tamper_framework.context import SQLContext, annotate_tokens_with_context, ClauseType


class TransformationRule:
    """
    Context-aware transformation rule
    
    CRITICAL FIXES:
    - Uses token.id instead of position for tracking
    - Can check SQL context before transforming
    - Prevents reapplication properly
    """
    
    def __init__(
        self,
        name: str,
        transform_func: Callable[[Token, SQLContext], Token],
        target_types: List[TokenType],
        skip_types: List[TokenType] = None,
        allowed_clauses: List[ClauseType] = None,  # NEW: context filtering
        track_transformed: bool = True
    ):
        self.name = name
        self.transform_func = transform_func
        self.target_types = target_types
        self.skip_types = skip_types or [TokenType.STRING_LITERAL, TokenType.COMMENT]
        self.allowed_clauses = allowed_clauses  # If set, only transform in these clauses
        self.track_transformed = track_transformed
        self.transformed_ids: Set[str] = set()  # Track by UUID, not position!
    
    def should_transform(self, token: Token, context: SQLContext) -> bool:
        """Check if token should be transformed"""
        # Skip if wrong type
        if token.type not in self.target_types:
            return False
        
        # Skip if in skip list
        if token.type in self.skip_types:
            return False
        
        # Skip if already transformed (use UUID!)
        if self.track_transformed and token.id in self.transformed_ids:
            return False
        
        # NEW: Check context if clause filtering is enabled
        if self.allowed_clauses and context.clause not in self.allowed_clauses:
            return False
        
        return True
    
    def apply(self, token: Token, context: SQLContext) -> Token:
        """Apply transformation to token"""
        if not self.should_transform(token, context):
            return token
        
        # Transform (pass context to transformation function)
        new_token = self.transform_func(token, context)
        
        # Track transformation by UUID
        if self.track_transformed:
            self.transformed_ids.add(token.id)
        
        return new_token
    
    def reset(self):
        """Reset transformation tracking"""
        self.transformed_ids.clear()


class SQLTransformer:
    """
    Context-aware SQL transformer
    
    Features:
    - UUID-based token tracking
    - SQL context awareness
    - Safe transformation ordering
    - Validation
    """
    
    def __init__(self):
        self.rules: List[TransformationRule] = []
        self.lexer = None
    
    def add_rule(self, rule: TransformationRule):
        """Add a transformation rule"""
        self.rules.append(rule)
    
    def transform(self, sql: str) -> str:
        """
        Transform SQL query using registered rules
        
        Process:
        1. Tokenize SQL
        2. Annotate tokens with context
        3. Apply each rule with context awareness
        4. Reconstruct SQL
        """
        # Tokenize
        self.lexer = SQLLexer(sql)
        tokens = self.lexer.tokenize()
        
        # Annotate with context
        annotated = annotate_tokens_with_context(tokens)
        
        # Apply each rule
        for rule in self.rules:
            annotated = self._apply_rule(annotated, rule)
        
        # Extract tokens (discard context)
        transformed_tokens = [token for token, _ in annotated]
        
        # Reconstruct
        result = self.lexer.reconstruct(transformed_tokens)
        
        # Reset rules for next transformation
        for rule in self.rules:
            rule.reset()
        
        return result
    
    def _apply_rule(
        self,
        annotated: List[tuple[Token, SQLContext]],
        rule: TransformationRule
    ) -> List[tuple[Token, SQLContext]]:
        """Apply a single rule to all tokens"""
        transformed = []
        
        for token, context in annotated:
            # Apply transformation with context
            new_token = rule.apply(token, context)
            transformed.append((new_token, context))
        
        return transformed


if __name__ == "__main__":
    # Test context-aware transformation
    
    def wrap_keyword(token: Token, context: SQLContext) -> Token:
        """Wrap keyword in MySQL version comment"""
        if token.type == TokenType.KEYWORD:
            new_value = f'/*!50000{token.value}*/'
            return Token(
                id=token.id,  # Keep same ID!
                type=token.type,
                value=new_value,
                position=token.position,
                line=token.line,
                column=token.column
            )
        return token
    
    # Create rule that only transforms in WHERE clause
    where_only_rule = TransformationRule(
        name="where_keyword_wrap",
        transform_func=wrap_keyword,
        target_types=[TokenType.KEYWORD],
        allowed_clauses=[ClauseType.WHERE],  # Only in WHERE!
        track_transformed=True
    )
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(where_only_rule)
    
    query = "SELECT * FROM users WHERE id=1 AND name='admin'"
    result = transformer.transform(query)
    
    print("Context-Aware Transformation Test")
    print("=" * 70)
    print(f"Original:    {query}")
    print(f"Transformed: {result}")
    print("\nNotice: Only WHERE and AND are wrapped (they're in WHERE clause)")
    print("SELECT and FROM are NOT wrapped (they're in SELECT/FROM clauses)")
