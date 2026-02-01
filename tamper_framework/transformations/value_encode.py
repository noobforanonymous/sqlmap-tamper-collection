#!/usr/bin/env python

"""
Value Encoding Transformation - FIXED VERSION

Properly encodes operators without breaking them.

CRITICAL FIX: Encodes entire operator, not individual characters
Example: '>=' becomes '%3E%3D', not '%3E='

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext, ClauseType


def create_value_encode_rule() -> TransformationRule:
    """
    Create a rule that properly encodes operators
    
    CRITICAL FIX: Encodes complete operators
    - '>=' -> '%3E%3D' (correct)
    - NOT '>=' -> '%3E=' (broken)
    
    Only encodes in WHERE/HAVING clauses (value context)
    """
    
    # Complete operator encoding map
    OPERATOR_ENCODING = {
        '=': '%3D',
        '<': '%3C',
        '>': '%3E',
        '!': '%21',
        '<=': '%3C%3D',  # Multi-char operators
        '>=': '%3E%3D',
        '<>': '%3C%3E',
        '!=': '%21%3D',
    }
    
    def encode_operator(token: Token, context: SQLContext) -> Token:
        """Encode operator - complete operator, not parts"""
        if token.type != TokenType.OPERATOR:
            return token
        
        # Only encode in value contexts (WHERE, HAVING)
        if context.clause not in (ClauseType.WHERE, ClauseType.HAVING):
            return token
        
        # Encode complete operator
        if token.value in OPERATOR_ENCODING:
            new_value = OPERATOR_ENCODING[token.value]
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
        name="value_encode",
        transform_func=encode_operator,
        target_types=[TokenType.OPERATOR],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        allowed_clauses=[ClauseType.WHERE, ClauseType.HAVING],  # Only in value context
        track_transformed=False  # Can encode multiple times
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    from tamper_framework.lexer import SQLLexer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_value_encode_rule())
    
    test_queries = [
        "SELECT * FROM users WHERE id>=5",
        "SELECT * FROM users WHERE id<=10",
        "SELECT * FROM users WHERE id<>1",
        "SELECT * FROM users WHERE name!='admin'"
    ]
    
    print("Testing Fixed Operator Encoding")
    print("=" * 70)
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
        
        # Verify operators are encoded correctly
        lexer = SQLLexer(result)
        tokens = lexer.tokenize()
        operators = [t.value for t in tokens if t.type == TokenType.OPERATOR]
        print(f"Operators:   {operators}")
