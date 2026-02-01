#!/usr/bin/env python

"""
Numeric Literal Obfuscation Transformation

Transforms numeric literals into equivalent but obfuscated forms.
Useful for bypassing WAFs that pattern-match on specific numbers.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext, ClauseType


def create_numeric_obfuscation_rule(style: str = "hex") -> TransformationRule:
    """
    Create a rule that obfuscates numeric literals
    
    Transformation styles:
        "hex"      -> 1 becomes 0x1
        "float"    -> 1 becomes 1.0 or 1e0
        "expr"     -> 1 becomes (1)
        "math"     -> 1 becomes (2-1) or (0+1)
        "binary"   -> 1 becomes 0b1
    
    Only transforms in WHERE/HAVING clauses (value context)
    """
    
    def to_hex(value: str) -> str:
        """Convert to hex literal"""
        try:
            num = int(float(value))
            if num >= 0:
                return f"0x{num:x}"
            return value
        except ValueError:
            return value
    
    def to_float(value: str) -> str:
        """Convert to float notation"""
        try:
            num = float(value)
            if num == int(num):
                return f"{int(num)}.0"
            return f"{num}"
        except ValueError:
            return value
    
    def to_scientific(value: str) -> str:
        """Convert to scientific notation"""
        try:
            num = float(value)
            return f"{num}e0"
        except ValueError:
            return value
    
    def to_expr(value: str) -> str:
        """Wrap in parentheses (expression)"""
        return f"({value})"
    
    def to_math(value: str) -> str:
        """Convert to math expression"""
        try:
            num = int(float(value))
            if num == 0:
                return "(1-1)"
            elif num == 1:
                return "(2-1)"
            elif num > 0:
                return f"({num + 1}-1)"
            else:
                return f"({num - 1}+1)"
        except ValueError:
            return value
    
    def to_binary(value: str) -> str:
        """Convert to binary literal (MySQL 5.0.3+)"""
        try:
            num = int(float(value))
            if num >= 0:
                return f"0b{bin(num)[2:]}"
            return value
        except ValueError:
            return value
    
    styles_map = {
        "hex": to_hex,
        "float": to_float,
        "scientific": to_scientific,
        "expr": to_expr,
        "math": to_math,
        "binary": to_binary
    }
    
    transform_func = styles_map.get(style, to_hex)
    
    def apply_numeric_obfuscation(token: Token, context: SQLContext) -> Token:
        """Obfuscate numeric literal"""
        if token.type != TokenType.NUMBER:
            return token
        
        # Only obfuscate in value contexts
        if context.clause not in (ClauseType.WHERE, ClauseType.HAVING, ClauseType.ON):
            return token
        
        # Skip if already obfuscated
        if token.value.startswith('0x') or token.value.startswith('0b'):
            return token
        
        new_value = transform_func(token.value)
        
        return Token(
            id=token.id,
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="numeric_obfuscation",
        transform_func=apply_numeric_obfuscation,
        target_types=[TokenType.NUMBER],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        allowed_clauses=[ClauseType.WHERE, ClauseType.HAVING, ClauseType.ON],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    query = "SELECT * FROM users WHERE id=1 AND status=0"
    
    for style in ["hex", "float", "math", "binary"]:
        transformer = SQLTransformer()
        transformer.add_rule(create_numeric_obfuscation_rule(style=style))
        result = transformer.transform(query)
        print(f"Style '{style}': {result}")
