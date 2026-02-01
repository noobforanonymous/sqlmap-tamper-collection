#!/usr/bin/env python

"""
Case Alternation Transformation - IMPROVED VERSION

Applies alternating case to SQL keywords with better detection.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext


def create_case_alternate_rule() -> TransformationRule:
    """
    Create a rule that applies alternating case to keywords
    
    Transformation:
        SELECT -> sElEcT
        WHERE -> wHeRe
    
    IMPROVED: Better detection of already-alternated keywords
    """
    
    def is_alternating_case(text: str) -> bool:
        """Check if text is already in alternating case"""
        if not text or len(text) < 2:
            return False
        
        # Check if follows pattern: lower, upper, lower, upper...
        for i, char in enumerate(text):
            if not char.isalpha():
                continue
            
            expected_lower = (i % 2 == 0)
            if expected_lower and char.isupper():
                return False
            if not expected_lower and char.islower():
                return False
        
        return True
    
    def alternate_case(token: Token, context: SQLContext) -> Token:
        """Apply alternating case to keyword"""
        if token.type != TokenType.KEYWORD:
            return token
        
        # Check if already alternated
        if is_alternating_case(token.value):
            return token
        
        # Apply alternating case
        new_value = ''.join(
            char.lower() if i % 2 == 0 else char.upper()
            for i, char in enumerate(token.value)
        )
        
        return Token(
            id=token.id,
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="case_alternate",
        transform_func=alternate_case,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_case_alternate_rule())
    
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "UNION SELECT password FROM admin"
    ]
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"Original:    {query}")
        print(f"Transformed: {result}\n")
