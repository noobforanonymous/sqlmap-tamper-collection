#!/usr/bin/env python

"""
Hex Encoding Transformation

Encodes string literals as hex values (0x...).
MySQL interprets hex as strings in string context.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext, ClauseType


def string_to_hex(s: str) -> str:
    """Convert string to MySQL hex literal"""
    # Remove quotes
    if s.startswith("'") and s.endswith("'"):
        content = s[1:-1]
    elif s.startswith('"') and s.endswith('"'):
        content = s[1:-1]
    else:
        content = s
    
    # Convert to hex
    hex_value = content.encode('utf-8').hex()
    return f"0x{hex_value}"


def create_hex_encode_rule() -> TransformationRule:
    """
    Create a rule that encodes string literals as hex
    
    Transformation:
        'admin' -> 0x61646d696e
        
    Features:
    - Only transforms strings in WHERE/HAVING
    - Preserves SQL validity (MySQL hex in string context)
    - Useful for bypassing quote-based filters
    """
    
    def apply_hex_encode(token: Token, context: SQLContext) -> Token:
        """Encode string literal as hex"""
        if token.type != TokenType.STRING_LITERAL:
            return token
        
        # Only encode in value contexts
        if context.clause not in (ClauseType.WHERE, ClauseType.HAVING, ClauseType.ON):
            return token
        
        # Skip empty strings
        if token.value in ("''", '""'):
            return token
        
        new_value = string_to_hex(token.value)
        
        return Token(
            id=token.id,
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="hex_encode",
        transform_func=apply_hex_encode,
        target_types=[TokenType.STRING_LITERAL],
        skip_types=[TokenType.COMMENT],
        allowed_clauses=[ClauseType.WHERE, ClauseType.HAVING, ClauseType.ON],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_hex_encode_rule())
    
    test_queries = [
        "SELECT * FROM users WHERE name='admin'",
        "SELECT * FROM users WHERE role='superuser' AND active='yes'",
    ]
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"Original:    {query}")
        print(f"Transformed: {result}\n")
