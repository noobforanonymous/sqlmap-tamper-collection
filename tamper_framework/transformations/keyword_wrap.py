#!/usr/bin/env python

"""
Keyword Wrapping Transformation

Wraps SQL keywords in MySQL version comments.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext


def create_keyword_wrap_rule() -> TransformationRule:
    """
    Create a rule that wraps keywords in MySQL version comments
    
    Transformation:
        SELECT -> /*!50000SELECT*/
        WHERE -> /*!50000WHERE*/
    
    Features:
    - Uses UUID tracking (no position bugs)
    - Checks if already wrapped
    - Works across all clauses
    """
    
    def wrap_keyword(token: Token, context: SQLContext) -> Token:
        """Wrap keyword in MySQL version comment"""
        if token.type != TokenType.KEYWORD:
            return token
        
        # Check if already wrapped
        if token.value.startswith('/*!'):
            return token
        
        new_value = f'/*!50000{token.value}*/'
        
        return Token(
            id=token.id,  # Keep same UUID
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="keyword_wrap",
        transform_func=wrap_keyword,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True  # Prevent double-wrapping
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "UNION SELECT password FROM admin"
    ]
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"Original:    {query}")
        print(f"Transformed: {result}\n")
