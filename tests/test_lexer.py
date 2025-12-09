#!/usr/bin/env python

"""
Comprehensive Lexer Tests

Tests all edge cases for the SQL lexer.

Author: Regaan
License: GPL v2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tamper_framework.lexer import SQLLexer, TokenType


def test_simple_select():
    """Test basic SELECT statement"""
    query = "SELECT * FROM users"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    assert len(tokens) == 8  # SELECT, space, *, space, FROM, space, users, EOF
    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[0].value == "SELECT"
    assert tokens[4].type == TokenType.KEYWORD
    assert tokens[4].value == "FROM"
    
    reconstructed = lexer.reconstruct(tokens)
    assert reconstructed == query
    print("✓ test_simple_select passed")


def test_multi_char_operators():
    """Test multi-character operators (CRITICAL)"""
    test_cases = [
        ("SELECT * FROM users WHERE id>=5", ">="),
        ("SELECT * FROM users WHERE id<=10", "<="),
        ("SELECT * FROM users WHERE id<>1", "<>"),
        ("SELECT * FROM users WHERE name!='admin'", "!="),
    ]
    
    for query, expected_op in test_cases:
        lexer = SQLLexer(query)
        tokens = lexer.tokenize()
        
        # Find the operator
        operators = [t for t in tokens if t.type == TokenType.OPERATOR and t.value == expected_op]
        assert len(operators) > 0, f"Expected operator {expected_op} not found in {query}"
        assert operators[0].value == expected_op, f"Operator broken: got {operators[0].value}, expected {expected_op}"
        
        # Verify reconstruction
        reconstructed = lexer.reconstruct(tokens)
        assert reconstructed == query, f"Reconstruction failed for {query}"
    
    print("✓ test_multi_char_operators passed")


def test_string_literals():
    """Test string literal handling"""
    query = "SELECT 'admin' FROM users"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    string_tokens = [t for t in tokens if t.type == TokenType.STRING_LITERAL]
    assert len(string_tokens) == 1
    assert string_tokens[0].value == "'admin'"
    
    reconstructed = lexer.reconstruct(tokens)
    assert reconstructed == query
    print("✓ test_string_literals passed")


def test_escaped_quotes():
    """Test escaped quotes in strings"""
    query = "SELECT 'it''s escaped' FROM users"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    string_tokens = [t for t in tokens if t.type == TokenType.STRING_LITERAL]
    assert len(string_tokens) == 1
    assert string_tokens[0].value == "'it''s escaped'"
    
    reconstructed = lexer.reconstruct(tokens)
    assert reconstructed == query
    print("✓ test_escaped_quotes passed")


def test_comments():
    """Test comment handling"""
    # Block comment
    query1 = "/* comment */ SELECT * FROM users"
    lexer1 = SQLLexer(query1)
    tokens1 = lexer1.tokenize()
    
    comment_tokens = [t for t in tokens1 if t.type == TokenType.COMMENT]
    assert len(comment_tokens) == 1
    assert comment_tokens[0].value == "/* comment */"
    assert lexer1.reconstruct(tokens1) == query1
    
    # Line comment
    query2 = "SELECT * FROM users -- comment"
    lexer2 = SQLLexer(query2)
    tokens2 = lexer2.tokenize()
    
    comment_tokens2 = [t for t in tokens2 if t.type == TokenType.COMMENT]
    assert len(comment_tokens2) == 1
    assert comment_tokens2[0].value == "-- comment"
    assert lexer2.reconstruct(tokens2) == query2
    
    print("✓ test_comments passed")


def test_complex_query():
    """Test complex query with multiple elements"""
    query = "SELECT user.id, user.name FROM users AS user WHERE user.role='admin' AND user.active=1"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    # Should tokenize without errors
    assert len(tokens) > 0
    
    # Test reconstruction
    reconstructed = lexer.reconstruct(tokens)
    assert reconstructed == query
    print("✓ test_complex_query passed")


def test_subquery():
    """Test subquery handling"""
    query = "SELECT * FROM (SELECT id FROM users) AS sub"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    # Should have parentheses
    lparen = [t for t in tokens if t.type == TokenType.LPAREN]
    rparen = [t for t in tokens if t.type == TokenType.RPAREN]
    assert len(lparen) == 1
    assert len(rparen) == 1
    
    # Test reconstruction
    reconstructed = lexer.reconstruct(tokens)
    assert reconstructed == query
    print("✓ test_subquery passed")


def test_uuid_uniqueness():
    """Test that each token gets unique UUID"""
    query = "SELECT * FROM users WHERE id=1"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    # Collect all UUIDs
    uuids = [t.id for t in tokens]
    
    # Check uniqueness
    assert len(uuids) == len(set(uuids)), "Token UUIDs are not unique!"
    print("✓ test_uuid_uniqueness passed")


def test_position_tracking():
    """Test position tracking"""
    query = "SELECT * FROM users"
    lexer = SQLLexer(query)
    tokens = lexer.tokenize()
    
    # First token should be at position 0
    assert tokens[0].position == 0
    
    # Positions should be increasing
    for i in range(len(tokens) - 1):
        if tokens[i].type != TokenType.EOF:
            assert tokens[i].position < tokens[i+1].position or tokens[i+1].type == TokenType.EOF
    
    print("✓ test_position_tracking passed")


def run_all_tests():
    """Run all lexer tests"""
    print("\n" + "=" * 70)
    print("Running Comprehensive Lexer Tests")
    print("=" * 70 + "\n")
    
    tests = [
        test_simple_select,
        test_multi_char_operators,
        test_string_literals,
        test_escaped_quotes,
        test_comments,
        test_complex_query,
        test_subquery,
        test_uuid_uniqueness,
        test_position_tracking,
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
