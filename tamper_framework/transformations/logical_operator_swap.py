#!/usr/bin/env python

"""
Logical Operator Swap Transformation

Swaps AND/OR with &&/|| equivalents in MySQL.
Useful for bypassing WAFs that block keyword-based logic.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext, ClauseType


# Logical operator mappings (MySQL)
LOGICAL_SWAP = {
    'AND': '&&',
    'OR': '||',
    'and': '&&',
    'or': '||',
    'And': '&&',
    'Or': '||',
}


def create_logical_swap_rule() -> TransformationRule:
    """
    Create a rule that swaps AND/OR with symbolic equivalents
    
    Transformation:
        AND -> &&
        OR  -> ||
        
    MySQL specific - these are equivalent operators.
    Only applies in WHERE/HAVING/ON clauses.
    """
    
    def apply_logical_swap(token: Token, context: SQLContext) -> Token:
        """Swap logical keywords with symbols"""
        if token.type != TokenType.KEYWORD:
            return token
        
        # Check if it's a logical operator
        if token.value.upper() not in ('AND', 'OR'):
            return token
        
        # Only swap in conditional clauses
        if context.clause not in (ClauseType.WHERE, ClauseType.HAVING, ClauseType.ON):
            return token
        
        # Get swap value
        new_value = LOGICAL_SWAP.get(token.value, token.value)
        
        return Token(
            id=token.id,
            type=TokenType.OPERATOR,  # Change type to operator
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="logical_swap",
        transform_func=apply_logical_swap,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        allowed_clauses=[ClauseType.WHERE, ClauseType.HAVING, ClauseType.ON],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_logical_swap_rule())
    
    test_queries = [
        "SELECT * FROM users WHERE id=1 AND active=1",
        "SELECT * FROM users WHERE role='admin' OR role='root'",
        "SELECT * FROM a JOIN b ON a.id=b.id AND a.x=1"
    ]
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"Original:    {query}")
        print(f"Transformed: {result}\n")
