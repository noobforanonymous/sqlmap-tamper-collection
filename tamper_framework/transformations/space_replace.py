#!/usr/bin/env python

"""
Space Replacement Transformation

Replaces spaces with inline comments.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext


def create_space_replace_rule() -> TransformationRule:
    """
    Create a rule that replaces spaces with inline comments
    
    Transformation:
        ' ' -> '/**/'
    
    Features:
    - Only replaces single spaces
    - Preserves newlines and tabs
    - Simple and deterministic
    """
    
    def replace_space(token: Token, context: SQLContext) -> Token:
        """Replace space with inline comment"""
        if token.type != TokenType.WHITESPACE:
            return token
        
        # Only replace single spaces, preserve newlines/tabs
        if token.value == ' ':
            new_value = '/**/'
            return Token(
                id=token.id,
                type=token.type,
                value=new_value,
                position=token.position,
                line=token.line,
                column=token.column
            )
        
        return token
    
    return TransformationRule(
        name="space_replace",
        transform_func=replace_space,
        target_types=[TokenType.WHITESPACE],
        skip_types=[],  # Don't skip anything for whitespace
        track_transformed=False  # Can apply multiple times
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_space_replace_rule())
    
    test_queries = [
        "SELECT * FROM users",
        "SELECT name FROM users WHERE id=1"
    ]
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"Original:    {query}")
        print(f"Transformed: {result}\n")
