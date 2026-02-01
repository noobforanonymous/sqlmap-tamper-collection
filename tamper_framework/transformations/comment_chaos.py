#!/usr/bin/env python

"""
Comment Chaos Transformation

Inserts randomized (but deterministic) comments between tokens.
Uses multiple comment styles to confuse WAF pattern matching.

Author: Regaan
License: GPL v2
"""

import hashlib
from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext


# Comment variants (MySQL compatible)
COMMENT_VARIANTS = [
    '/**/',       # Standard inline
    '/*foo*/',    # With content
    '/*!*/',      # MySQL conditional (empty)
    '/*! */',     # MySQL conditional with space
    '/*--*/',     # Nested looking
    '/*/*/',      # Nested attempt
]


def create_comment_chaos_rule(seed: str = "tamper") -> TransformationRule:
    """
    Create a rule that inserts varied comments between tokens
    
    Transformation:
        ' ' -> various comment styles
        
    Features:
    - Multiple comment formats
    - Deterministic based on token position (reproducible)
    - Never modifies content inside strings
    - Uses seed for consistent output
    """
    
    def get_comment_variant(token_id: str, seed: str) -> str:
        """Get deterministic comment variant based on token ID"""
        # Hash token ID + seed for deterministic but varied selection
        hash_input = f"{token_id}{seed}".encode()
        hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
        index = hash_val % len(COMMENT_VARIANTS)
        return COMMENT_VARIANTS[index]
    
    def apply_comment_chaos(token: Token, context: SQLContext) -> Token:
        """Replace whitespace with varied comments"""
        if token.type != TokenType.WHITESPACE:
            return token
        
        # Only replace single spaces
        if token.value != ' ':
            return token
        
        # Get deterministic comment variant
        comment = get_comment_variant(token.id, seed)
        
        return Token(
            id=token.id,
            type=token.type,
            value=comment,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="comment_chaos",
        transform_func=apply_comment_chaos,
        target_types=[TokenType.WHITESPACE],
        skip_types=[],  # Don't skip anything for whitespace
        track_transformed=False  # Can apply multiple times
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_comment_chaos_rule(seed="test123"))
    
    query = "SELECT * FROM users WHERE id=1"
    result = transformer.transform(query)
    
    print(f"Original:    {query}")
    print(f"Transformed: {result}")
    
    # Test determinism
    result2 = transformer.transform(query)
    print(f"Same again:  {result2}")
    print(f"Deterministic: {result == result2}")
