#!/usr/bin/env python

"""
Comprehensive Transformer Tests

Tests context-aware transformations.

Author: Regaan
License: GPL v2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import (
    create_keyword_wrap_rule,
    create_space_replace_rule,
    create_case_alternate_rule,
    create_value_encode_rule
)
from tamper_framework.lexer import SQLLexer, TokenType


def test_keyword_wrap():
    """Test keyword wrapping transformation"""
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    assert "/*!50000SELECT*/" in result
    assert "/*!50000FROM*/" in result
    print("✓ test_keyword_wrap passed")


def test_space_replace():
    """Test space replacement transformation"""
    transformer = SQLTransformer()
    transformer.add_rule(create_space_replace_rule())
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    assert "/**/" in result
    # Check that spaces are replaced
    assert result.count("/**/") >= 3  # At least 3 spaces replaced
    print("✓ test_space_replace passed")


def test_case_alternate():
    """Test case alternation transformation"""
    transformer = SQLTransformer()
    transformer.add_rule(create_case_alternate_rule())
    
    query = "SELECT FROM WHERE"
    result = transformer.transform(query)
    
    assert "sElEcT" in result
    assert "fRoM" in result
    assert "wHeRe" in result
    print("✓ test_case_alternate passed")


def test_value_encode():
    """Test value encoding transformation (CRITICAL)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_value_encode_rule())
    
    # Test single char operator
    query1 = "SELECT * FROM users WHERE id=1"
    result1 = transformer.transform(query1)
    assert "%3D" in result1  # = encoded
    
    # Test multi-char operators (CRITICAL FIX)
    query2 = "SELECT * FROM users WHERE id>=5"
    result2 = transformer.transform(query2)
    assert "%3E%3D" in result2  # >= encoded completely
    assert "%3E=" not in result2  # NOT broken encoding
    
    query3 = "SELECT * FROM users WHERE id<=10"
    result3 = transformer.transform(query3)
    assert "%3C%3D" in result3  # <= encoded completely
    
    query4 = "SELECT * FROM users WHERE id<>1"
    result4 = transformer.transform(query4)
    assert "%3C%3E" in result4  # <> encoded completely
    
    print("✓ test_value_encode passed")


def test_combined_transformations():
    """Test multiple transformations together"""
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    transformer.add_rule(create_space_replace_rule())
    transformer.add_rule(create_value_encode_rule())
    transformer.add_rule(create_case_alternate_rule())
    
    query = "SELECT * FROM users WHERE id=1"
    result = transformer.transform(query)
    
    # Should have all transformations
    assert "/*!50000" in result  # Keywords wrapped
    assert "/**/" in result  # Spaces replaced
    assert "%3D" in result  # Operators encoded
    # Case should be alternated inside comments
    
    print("✓ test_combined_transformations passed")


def test_string_preservation():
    """Test that string literals are preserved"""
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    transformer.add_rule(create_space_replace_rule())
    
    query = "SELECT * FROM users WHERE name='admin'"
    result = transformer.transform(query)
    
    # String literal should be unchanged
    assert "'admin'" in result
    print("✓ test_string_preservation passed")


def test_comment_preservation():
    """Test that comments are preserved"""
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    
    query = "/* comment */ SELECT * FROM users"
    result = transformer.transform(query)
    
    # Comment should be unchanged
    assert "/* comment */" in result
    print("✓ test_comment_preservation passed")


def test_context_awareness():
    """Test context-aware encoding (only in WHERE clause)"""
    transformer = SQLTransformer()
    transformer.add_rule(create_value_encode_rule())
    
    query = "SELECT * FROM users WHERE id=1"
    result = transformer.transform(query)
    
    # = in WHERE should be encoded
    assert "%3D" in result
    
    # * in SELECT should NOT be encoded (it's not in WHERE)
    lexer = SQLLexer(result)
    tokens = lexer.tokenize()
    star_tokens = [t for t in tokens if t.value == '*']
    assert len(star_tokens) > 0, "Star should be preserved"
    
    print("✓ test_context_awareness passed")


def test_deterministic_output():
    """Test that transformation is deterministic"""
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    transformer.add_rule(create_space_replace_rule())
    transformer.add_rule(create_value_encode_rule())
    transformer.add_rule(create_case_alternate_rule())
    
    query = "SELECT * FROM users WHERE id=1"
    
    result1 = transformer.transform(query)
    result2 = transformer.transform(query)
    
    assert result1 == result2, "Transformation is not deterministic!"
    print("✓ test_deterministic_output passed")


def test_no_reapplication():
    """Test that transformations don't reapply"""
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    
    query = "SELECT * FROM users"
    result1 = transformer.transform(query)
    result2 = transformer.transform(result1)  # Transform again
    
    # Should not double-wrap
    assert result1 == result2 or "/*!50000/*!50000" not in result2
    print("✓ test_no_reapplication passed")


def run_all_tests():
    """Run all transformer tests"""
    print("\n" + "=" * 70)
    print("Running Comprehensive Transformer Tests")
    print("=" * 70 + "\n")
    
    tests = [
        test_keyword_wrap,
        test_space_replace,
        test_case_alternate,
        test_value_encode,
        test_combined_transformations,
        test_string_preservation,
        test_comment_preservation,
        test_context_awareness,
        test_deterministic_output,
        test_no_reapplication,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
