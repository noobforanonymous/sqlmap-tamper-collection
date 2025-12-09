#!/usr/bin/env python

"""
SQL Context Tracker - Tracks SQL clause state and nesting

This is critical for context-aware transformations.
We need to know if we're in SELECT, WHERE, FROM, etc.

Author: Regaan
License: GPL v2
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from tamper_framework.lexer import Token, TokenType


class ClauseType(Enum):
    """SQL clause types"""
    UNKNOWN = "UNKNOWN"
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    JOIN = "JOIN"
    ON = "ON"
    GROUP_BY = "GROUP_BY"
    HAVING = "HAVING"
    ORDER_BY = "ORDER_BY"
    LIMIT = "LIMIT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VALUES = "VALUES"
    SET = "SET"
    UNION = "UNION"


@dataclass
class SQLContext:
    """
    Represents the current SQL parsing context
    
    Tracks:
    - Current clause (SELECT, WHERE, etc.)
    - Nesting depth (for subqueries)
    - Function call depth
    - Parent context (for nested structures)
    """
    clause: ClauseType
    depth: int  # Parenthesis nesting level
    in_function: bool
    in_subquery: bool
    parent: Optional['SQLContext'] = None
    
    def __repr__(self):
        return f"Context({self.clause.value}, depth={self.depth}, subquery={self.in_subquery})"


class SQLContextTracker:
    """
    Tracks SQL context as we process tokens
    
    This allows transformations to be context-aware:
    - Don't encode operators in SELECT clause
    - Do encode operators in WHERE clause
    - Handle subqueries correctly
    - Track function calls
    """
    
    # Keywords that start new clauses
    CLAUSE_KEYWORDS = {
        'SELECT': ClauseType.SELECT,
        'FROM': ClauseType.FROM,
        'WHERE': ClauseType.WHERE,
        'JOIN': ClauseType.JOIN,
        'INNER': ClauseType.JOIN,
        'LEFT': ClauseType.JOIN,
        'RIGHT': ClauseType.JOIN,
        'OUTER': ClauseType.JOIN,
        'ON': ClauseType.ON,
        'GROUP': ClauseType.GROUP_BY,
        'HAVING': ClauseType.HAVING,
        'ORDER': ClauseType.ORDER_BY,
        'LIMIT': ClauseType.LIMIT,
        'INSERT': ClauseType.INSERT,
        'UPDATE': ClauseType.UPDATE,
        'DELETE': ClauseType.DELETE,
        'VALUES': ClauseType.VALUES,
        'SET': ClauseType.SET,
        'UNION': ClauseType.UNION,
    }
    
    # Function keywords (common SQL functions)
    FUNCTION_KEYWORDS = {
        'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CONCAT', 'SUBSTRING',
        'UPPER', 'LOWER', 'TRIM', 'LENGTH', 'COALESCE', 'IFNULL',
        'CAST', 'CONVERT', 'DATE', 'NOW', 'CURDATE', 'CURTIME'
    }
    
    def __init__(self):
        self.current_context = SQLContext(
            clause=ClauseType.UNKNOWN,
            depth=0,
            in_function=False,
            in_subquery=False
        )
        self.context_stack: List[SQLContext] = []
    
    def process_token(self, token: Token) -> SQLContext:
        """
        Process a token and update context
        
        Returns the current context after processing this token
        """
        # Handle parentheses (subqueries and functions)
        if token.type == TokenType.LPAREN:
            self._handle_lparen(token)
        elif token.type == TokenType.RPAREN:
            self._handle_rparen(token)
        
        # Handle clause keywords
        elif token.type == TokenType.KEYWORD:
            self._handle_keyword(token)
        
        return self.current_context
    
    def _handle_lparen(self, token: Token):
        """Handle opening parenthesis"""
        # Save current context
        self.context_stack.append(self.current_context)
        
        # Create new context with increased depth
        self.current_context = SQLContext(
            clause=self.current_context.clause,
            depth=self.current_context.depth + 1,
            in_function=self.current_context.in_function,
            in_subquery=False,  # Will be set if we see SELECT
            parent=self.current_context
        )
    
    def _handle_rparen(self, token: Token):
        """Handle closing parenthesis"""
        # Restore previous context
        if self.context_stack:
            self.current_context = self.context_stack.pop()
    
    def _handle_keyword(self, token: Token):
        """Handle SQL keyword"""
        keyword = token.value.upper()
        
        # Check if it's a clause keyword
        if keyword in self.CLAUSE_KEYWORDS:
            new_clause = self.CLAUSE_KEYWORDS[keyword]
            
            # If we see SELECT inside parentheses, it's a subquery
            if keyword == 'SELECT' and self.current_context.depth > 0:
                self.current_context = SQLContext(
                    clause=new_clause,
                    depth=self.current_context.depth,
                    in_function=False,
                    in_subquery=True,
                    parent=self.current_context.parent
                )
            else:
                # Normal clause change
                self.current_context = SQLContext(
                    clause=new_clause,
                    depth=self.current_context.depth,
                    in_function=self.current_context.in_function,
                    in_subquery=self.current_context.in_subquery,
                    parent=self.current_context.parent
                )
        
        # Check if it's a function
        elif keyword in self.FUNCTION_KEYWORDS:
            self.current_context.in_function = True
    
    def get_context(self) -> SQLContext:
        """Get current context"""
        return self.current_context
    
    def is_in_where_clause(self) -> bool:
        """Check if currently in WHERE clause"""
        return self.current_context.clause == ClauseType.WHERE
    
    def is_in_select_clause(self) -> bool:
        """Check if currently in SELECT clause"""
        return self.current_context.clause == ClauseType.SELECT
    
    def is_in_subquery(self) -> bool:
        """Check if currently in a subquery"""
        return self.current_context.in_subquery
    
    def get_depth(self) -> int:
        """Get current nesting depth"""
        return self.current_context.depth


def annotate_tokens_with_context(tokens: List[Token]) -> List[tuple[Token, SQLContext]]:
    """
    Annotate each token with its SQL context
    
    Returns list of (token, context) tuples
    """
    tracker = SQLContextTracker()
    annotated = []
    
    for token in tokens:
        context = tracker.process_token(token)
        annotated.append((token, context))
    
    return annotated


if __name__ == "__main__":
    from tamper_framework.lexer import SQLLexer
    
    # Test context tracking
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "SELECT * FROM (SELECT id FROM users) AS sub WHERE id>5",
        "SELECT COUNT(*) FROM users WHERE active=1",
        "UPDATE users SET name='admin' WHERE id=1"
    ]
    
    print("Testing SQL Context Tracking")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        
        # Tokenize
        lexer = SQLLexer(query)
        tokens = lexer.tokenize()
        
        # Annotate with context
        annotated = annotate_tokens_with_context(tokens)
        
        # Show context for important tokens
        for token, context in annotated:
            if token.type in (TokenType.KEYWORD, TokenType.OPERATOR):
                print(f"{token.value:15} -> {context}")
