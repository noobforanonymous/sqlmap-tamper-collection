#!/usr/bin/env python

"""
Variable Version Comment Transformation

Uses various MySQL version comment numbers instead of fixed 50000.
Different versions can bypass different WAF rules.

Author: Regaan
License: GPL v2
"""

import hashlib
from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext


# MySQL version numbers that are commonly accepted
# Format: /*!NNNNN keyword*/ where NNNNN is version
VERSION_NUMBERS = [
    '50000',  # 5.0.0
    '50001',  # 5.0.1
    '50100',  # 5.1.0
    '50500',  # 5.5.0
    '50600',  # 5.6.0
    '50700',  # 5.7.0
    '80000',  # 8.0.0
    '80017',  # 8.0.17
    '80023',  # 8.0.23
]


def create_version_comment_vary_rule(fixed_version: str = None) -> TransformationRule:
    """
    Create a rule that wraps keywords with varied version comments
    
    Transformation:
        SELECT -> /*!50700SELECT*/ (varies)
        
    If fixed_version is provided, uses that version.
    Otherwise, deterministically varies based on token position.
    """
    
    def get_version(token_id: str) -> str:
        """Get deterministic version based on token ID"""
        if fixed_version:
            return fixed_version
        hash_val = int(hashlib.md5(token_id.encode()).hexdigest(), 16)
        return VERSION_NUMBERS[hash_val % len(VERSION_NUMBERS)]
    
    def apply_version_wrap(token: Token, context: SQLContext) -> Token:
        """Wrap keyword with version comment"""
        if token.type != TokenType.KEYWORD:
            return token
        
        # Skip if already wrapped
        if token.value.startswith('/*!'):
            return token
        
        version = get_version(token.id)
        new_value = f"/*!{version}{token.value}*/"
        
        return Token(
            id=token.id,
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="version_comment_vary",
        transform_func=apply_version_wrap,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test varied versions
    transformer = SQLTransformer()
    transformer.add_rule(create_version_comment_vary_rule())
    
    query = "SELECT * FROM users WHERE id=1 AND active=1"
    result = transformer.transform(query)
    print(f"Varied:    {result}")
    
    # Test fixed version
    transformer2 = SQLTransformer()
    transformer2.add_rule(create_version_comment_vary_rule(fixed_version="50700"))
    result2 = transformer2.transform(query)
    print(f"Fixed:     {result2}")
