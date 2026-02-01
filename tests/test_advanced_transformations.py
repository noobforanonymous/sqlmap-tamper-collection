#!/usr/bin/env python
"""
Tests for Advanced Transformation Modules

Tests the new v2.1.0 transformation rules:
- Homoglyphs
- Function wrapping
- Numeric obfuscation
- Comment chaos
- Logical swap
- Hex encoding
- Version comment variation

Author: Regaan
License: GPL v2
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import (
    create_homoglyph_rule,
    create_function_wrap_rule,
    create_numeric_obfuscation_rule,
    create_comment_chaos_rule,
    create_logical_swap_rule,
    create_hex_encode_rule,
    create_version_comment_vary_rule,
)


def test_homoglyph_rule():
    """Test homoglyph substitution"""
    transformer = SQLTransformer()
    transformer.add_rule(create_homoglyph_rule(aggressive=False))
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    # Result should be different (contains Unicode)
    assert result != query
    
    # Should still be "readable" as SELECT (contain S, L, C, T)
    upper_result = result.upper()
    assert 'S' in upper_result or 'S' in result
    
    # Bytes should be different (Unicode chars are multi-byte)
    assert len(result.encode('utf-8')) >= len(query.encode('utf-8'))
    
    print("✓ test_homoglyph_rule passed")


def test_function_wrap_rule():
    """Test function wrapping (IF style)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_function_wrap_rule(wrap_style="if"))
    
    query = "UNION SELECT password FROM admin"
    result = transformer.transform(query)
    
    # UNION and SELECT should be wrapped
    assert "IF(1," in result
    assert ",1)" in result
    
    print("✓ test_function_wrap_rule passed")


def test_function_wrap_case_style():
    """Test function wrapping (CASE style)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_function_wrap_rule(wrap_style="case"))
    
    query = "UNION SELECT password"
    result = transformer.transform(query)
    
    # Should contain CASE WHEN
    assert "CASE WHEN 1 THEN" in result
    assert "END" in result
    
    print("✓ test_function_wrap_case_style passed")


def test_numeric_obfuscation_hex():
    """Test numeric obfuscation (hex style)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_numeric_obfuscation_rule(style="hex"))
    
    query = "SELECT * FROM users WHERE id=1"
    result = transformer.transform(query)
    
    # 1 should become 0x1
    assert "0x1" in result
    assert "=1" not in result or "%3D1" not in result
    
    print("✓ test_numeric_obfuscation_hex passed")


def test_numeric_obfuscation_math():
    """Test numeric obfuscation (math style)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_numeric_obfuscation_rule(style="math"))
    
    query = "SELECT * FROM users WHERE id=1"
    result = transformer.transform(query)
    
    # 1 should become (2-1)
    assert "(2-1)" in result
    
    print("✓ test_numeric_obfuscation_math passed")


def test_numeric_obfuscation_float():
    """Test numeric obfuscation (float style)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_numeric_obfuscation_rule(style="float"))
    
    query = "SELECT * FROM users WHERE id=1"
    result = transformer.transform(query)
    
    # 1 should become 1.0
    assert "1.0" in result
    
    print("✓ test_numeric_obfuscation_float passed")


def test_comment_chaos():
    """Test comment chaos (varied comments)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_comment_chaos_rule(seed="test"))
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    # Spaces should be replaced with comments
    assert "/**/" in result or "/*foo*/" in result or "/*!*/" in result
    
    print("✓ test_comment_chaos passed")


def test_comment_chaos_determinism():
    """Test that comment chaos is deterministic"""
    seed = "consistent_seed"
    query = "SELECT * FROM users WHERE id=1"
    
    # Transform twice with same seed
    t1 = SQLTransformer()
    t1.add_rule(create_comment_chaos_rule(seed=seed))
    result1 = t1.transform(query)
    
    t2 = SQLTransformer()
    t2.add_rule(create_comment_chaos_rule(seed=seed))
    result2 = t2.transform(query)
    
    # Results should be identical
    assert result1 == result2
    
    print("✓ test_comment_chaos_determinism passed")


def test_logical_swap():
    """Test AND/OR to &&/|| swap"""
    transformer = SQLTransformer()
    transformer.add_rule(create_logical_swap_rule())
    
    query = "SELECT * FROM users WHERE id=1 AND active=1"
    result = transformer.transform(query)
    
    # AND should become &&
    assert "&&" in result
    assert " AND " not in result.upper() or "AND" not in result.split()
    
    print("✓ test_logical_swap passed")


def test_logical_swap_or():
    """Test OR swap"""
    transformer = SQLTransformer()
    transformer.add_rule(create_logical_swap_rule())
    
    query = "SELECT * FROM users WHERE role='admin' OR role='root'"
    result = transformer.transform(query)
    
    # OR should become ||
    assert "||" in result
    
    print("✓ test_logical_swap_or passed")


def test_hex_encode():
    """Test string to hex encoding"""
    transformer = SQLTransformer()
    transformer.add_rule(create_hex_encode_rule())
    
    query = "SELECT * FROM users WHERE name='admin'"
    result = transformer.transform(query)
    
    # 'admin' should become 0x61646d696e
    assert "0x61646d696e" in result
    assert "'admin'" not in result
    
    print("✓ test_hex_encode passed")


def test_hex_encode_preserves_select():
    """Test that hex encoding only affects WHERE, not table names"""
    transformer = SQLTransformer()
    transformer.add_rule(create_hex_encode_rule())
    
    # 'users' in FROM should not be encoded (it's not a string literal in WHERE)
    query = "SELECT * FROM users WHERE name='test'"
    result = transformer.transform(query)
    
    # 'test' should be hex
    assert "0x74657374" in result
    # users is an identifier, not affected
    assert "users" in result
    
    print("✓ test_hex_encode_preserves_select passed")


def test_version_comment_vary():
    """Test variable version comments"""
    transformer = SQLTransformer()
    transformer.add_rule(create_version_comment_vary_rule())
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    # Should have version comments with various numbers
    assert "/*!" in result
    assert "*/" in result
    
    print("✓ test_version_comment_vary passed")


def test_version_comment_fixed():
    """Test fixed version number"""
    transformer = SQLTransformer()
    transformer.add_rule(create_version_comment_vary_rule(fixed_version="50700"))
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    # All comments should use 50700
    assert "/*!50700" in result
    
    print("✓ test_version_comment_fixed passed")


def test_combined_aws_waf_chain():
    """Test AWS WAF style chain"""
    transformer = SQLTransformer()
    transformer.add_rule(create_logical_swap_rule())
    transformer.add_rule(create_version_comment_vary_rule(fixed_version="50700"))
    transformer.add_rule(create_hex_encode_rule())
    transformer.add_rule(create_numeric_obfuscation_rule(style="hex"))
    
    query = "SELECT * FROM users WHERE id=1 AND name='admin'"
    result = transformer.transform(query)
    
    # Should have all transformations
    assert "&&" in result  # Logical swap
    assert "/*!50700" in result  # Version comments
    assert "0x61646d696e" in result  # Hex string
    assert "0x1" in result  # Hex number
    
    print("✓ test_combined_aws_waf_chain passed")


def test_combined_imperva_chain():
    """Test Imperva style chain"""
    transformer = SQLTransformer()
    transformer.add_rule(create_homoglyph_rule())
    transformer.add_rule(create_function_wrap_rule(wrap_style="if"))
    
    query = "UNION SELECT password"
    result = transformer.transform(query)
    
    # Should have function wrapping
    assert "IF(1," in result
    
    # Result should be different due to homoglyphs
    # (function wrap first, then homoglyphs might affect keywords inside IF)
    assert result != query
    
    print("✓ test_combined_imperva_chain passed")


def run_all_tests():
    """Run all advanced transformation tests"""
    print("\n" + "=" * 70)
    print("Running Advanced Transformation Tests (v2.1.0)")
    print("=" * 70 + "\n")
    
    tests = [
        test_homoglyph_rule,
        test_function_wrap_rule,
        test_function_wrap_case_style,
        test_numeric_obfuscation_hex,
        test_numeric_obfuscation_math,
        test_numeric_obfuscation_float,
        test_comment_chaos,
        test_comment_chaos_determinism,
        test_logical_swap,
        test_logical_swap_or,
        test_hex_encode,
        test_hex_encode_preserves_select,
        test_version_comment_vary,
        test_version_comment_fixed,
        test_combined_aws_waf_chain,
        test_combined_imperva_chain,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
    
    print("\n" + "-" * 70)
    print(f"Results: {passed}/{len(tests)} passed, {failed} failed")
    print("-" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
