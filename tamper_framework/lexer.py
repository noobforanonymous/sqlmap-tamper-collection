#!/usr/bin/env python

"""
SQL Lexer - Tokenizes SQL queries with proper tracking

Author: Regaan
License: GPL v2
"""

import re
import uuid
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    """SQL token types"""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    STRING_LITERAL = "STRING_LITERAL"
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"
    UNKNOWN = "UNKNOWN"
    EOF = "EOF"

@dataclass
class Token:
    """
    Represents a single SQL token with unique ID
    
    CRITICAL: Uses UUID for tracking, not position
    Position can change after transformations
    """
    id: str  # Unique identifier for tracking
    type: TokenType
    value: str
    position: int  # Original position (for reconstruction)
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.value}, {repr(self.value)}, id={self.id[:8]}...)"

class SQLLexer:
    """
    SQL lexer with UUID-based token tracking
    
    Features:
    - Each token gets unique ID
    - Handles escaped quotes in strings
    - Preserves comments
    - Multi-character operator support
    - Line and column tracking
    """
    
    # SQL keywords (MySQL/MariaDB focused)
    KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'DROP',
        'CREATE', 'ALTER', 'TRUNCATE', 'UNION', 'JOIN', 'INNER', 'OUTER',
        'LEFT', 'RIGHT', 'CROSS', 'NATURAL', 'ON', 'USING', 'ORDER', 'GROUP',
        'BY', 'HAVING', 'LIMIT', 'OFFSET', 'AS', 'AND', 'OR', 'NOT', 'IN',
        'LIKE', 'BETWEEN', 'IS', 'NULL', 'TRUE', 'FALSE', 'CASE', 'WHEN',
        'THEN', 'ELSE', 'END', 'EXISTS', 'ALL', 'ANY', 'SOME', 'DISTINCT',
        'INTO', 'VALUES', 'SET', 'TABLE', 'DATABASE', 'INDEX', 'VIEW',
        'PROCEDURE', 'FUNCTION', 'TRIGGER', 'EVENT', 'GRANT', 'REVOKE',
        'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'START', 'TRANSACTION',
        'LOCK', 'UNLOCK', 'DESCRIBE', 'EXPLAIN', 'SHOW', 'USE'
    }
    
    # Multi-character operators (check these FIRST)
    MULTI_CHAR_OPERATORS = [
        '<=', '>=', '<>', '!=', '||', '&&', '<<', '>>'
    ]
    
    # Single character operators
    SINGLE_CHAR_OPERATORS = {
        '=', '<', '>', '+', '-', '*', '/', '%', '!', '~', '&', '|', '^'
    }
    
    def __init__(self, sql: str):
        self.sql = sql
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get current character without advancing"""
        if self.position >= len(self.sql):
            return None
        return self.sql[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Look ahead without advancing"""
        pos = self.position + offset
        if pos >= len(self.sql):
            return None
        return self.sql[pos]
    
    def peek_string(self, length: int) -> str:
        """Look ahead multiple characters"""
        return self.sql[self.position:self.position + length]
    
    def advance(self) -> Optional[str]:
        """Move to next character and return it"""
        if self.position >= len(self.sql):
            return None
        
        char = self.sql[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self) -> str:
        """Collect whitespace characters"""
        start_pos = self.position
        start_line = self.line
        start_col = self.column
        whitespace = ""
        
        while self.current_char() and self.current_char() in ' \t\n\r':
            whitespace += self.current_char()
            self.advance()
        
        if whitespace:
            self.tokens.append(Token(
                id=str(uuid.uuid4()),
                type=TokenType.WHITESPACE,
                value=whitespace,
                position=start_pos,
                line=start_line,
                column=start_col
            ))
        
        return whitespace
    
    def read_string_literal(self, quote_char: str) -> Token:
        """Read a string literal with proper escape handling"""
        start_pos = self.position
        start_line = self.line
        start_col = self.column
        value = quote_char
        self.advance()  # Skip opening quote
        
        while self.current_char():
            char = self.current_char()
            
            # Handle escape sequences
            if char == '\\':
                value += char
                self.advance()
                if self.current_char():
                    value += self.current_char()
                    self.advance()
                continue
            
            # Handle doubled quotes (SQL escape: '' or "")
            if char == quote_char:
                value += char
                self.advance()
                
                # Check if it's a doubled quote (escape)
                if self.current_char() == quote_char:
                    value += char
                    self.advance()
                    continue
                else:
                    # End of string
                    break
            
            value += char
            self.advance()
        
        return Token(
            id=str(uuid.uuid4()),
            type=TokenType.STRING_LITERAL,
            value=value,
            position=start_pos,
            line=start_line,
            column=start_col
        )
    
    def read_comment(self) -> Token:
        """Read SQL comment (-- or /* ... */)"""
        start_pos = self.position
        start_line = self.line
        start_col = self.column
        
        # Line comment: --
        if self.current_char() == '-' and self.peek_char() == '-':
            value = ""
            while self.current_char() and self.current_char() != '\n':
                value += self.current_char()
                self.advance()
            return Token(
                id=str(uuid.uuid4()),
                type=TokenType.COMMENT,
                value=value,
                position=start_pos,
                line=start_line,
                column=start_col
            )
        
        # Block comment: /* ... */
        if self.current_char() == '/' and self.peek_char() == '*':
            value = ""
            value += self.advance()  # /
            value += self.advance()  # *
            
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    value += self.advance()  # *
                    value += self.advance()  # /
                    break
                value += self.advance()
            
            return Token(
                id=str(uuid.uuid4()),
                type=TokenType.COMMENT,
                value=value,
                position=start_pos,
                line=start_line,
                column=start_col
            )
        
        return None
    
    def read_identifier_or_keyword(self) -> Token:
        """Read identifier or keyword"""
        start_pos = self.position
        start_line = self.line
        start_col = self.column
        value = ""
        
        # Read alphanumeric and underscore
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = TokenType.KEYWORD if value.upper() in self.KEYWORDS else TokenType.IDENTIFIER
        
        return Token(
            id=str(uuid.uuid4()),
            type=token_type,
            value=value,
            position=start_pos,
            line=start_line,
            column=start_col
        )
    
    def read_number(self) -> Token:
        """Read numeric literal"""
        start_pos = self.position
        start_line = self.line
        start_col = self.column
        value = ""
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            value += self.current_char()
            self.advance()
        
        return Token(
            id=str(uuid.uuid4()),
            type=TokenType.NUMBER,
            value=value,
            position=start_pos,
            line=start_line,
            column=start_col
        )
    
    def read_operator(self) -> Token:
        """
        Read operator with proper multi-character support
        
        CRITICAL FIX: Check multi-char operators FIRST
        This prevents breaking >= into > and =
        """
        start_pos = self.position
        start_line = self.line
        start_col = self.column
        
        # Check multi-character operators first (IMPORTANT!)
        for op in self.MULTI_CHAR_OPERATORS:
            if self.peek_string(len(op)) == op:
                value = op
                for _ in range(len(op)):
                    self.advance()
                return Token(
                    id=str(uuid.uuid4()),
                    type=TokenType.OPERATOR,
                    value=value,
                    position=start_pos,
                    line=start_line,
                    column=start_col
                )
        
        # Single character operator
        value = self.current_char()
        self.advance()
        return Token(
            id=str(uuid.uuid4()),
            type=TokenType.OPERATOR,
            value=value,
            position=start_pos,
            line=start_line,
            column=start_col
        )
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire SQL query"""
        self.tokens = []
        
        while self.current_char():
            char = self.current_char()
            
            # Whitespace
            if char in ' \t\n\r':
                self.skip_whitespace()
                continue
            
            # String literals
            if char in ('"', "'"):
                self.tokens.append(self.read_string_literal(char))
                continue
            
            # Comments
            if char == '-' and self.peek_char() == '-':
                self.tokens.append(self.read_comment())
                continue
            
            if char == '/' and self.peek_char() == '*':
                self.tokens.append(self.read_comment())
                continue
            
            # Numbers
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier_or_keyword())
                continue
            
            # Special characters
            if char == '(':
                self.tokens.append(Token(
                    id=str(uuid.uuid4()),
                    type=TokenType.LPAREN,
                    value=char,
                    position=self.position,
                    line=self.line,
                    column=self.column
                ))
                self.advance()
                continue
            
            if char == ')':
                self.tokens.append(Token(
                    id=str(uuid.uuid4()),
                    type=TokenType.RPAREN,
                    value=char,
                    position=self.position,
                    line=self.line,
                    column=self.column
                ))
                self.advance()
                continue
            
            if char == ',':
                self.tokens.append(Token(
                    id=str(uuid.uuid4()),
                    type=TokenType.COMMA,
                    value=char,
                    position=self.position,
                    line=self.line,
                    column=self.column
                ))
                self.advance()
                continue
            
            if char == ';':
                self.tokens.append(Token(
                    id=str(uuid.uuid4()),
                    type=TokenType.SEMICOLON,
                    value=char,
                    position=self.position,
                    line=self.line,
                    column=self.column
                ))
                self.advance()
                continue
            
            if char == '.':
                self.tokens.append(Token(
                    id=str(uuid.uuid4()),
                    type=TokenType.DOT,
                    value=char,
                    position=self.position,
                    line=self.line,
                    column=self.column
                ))
                self.advance()
                continue
            
            # Operators (check this AFTER special chars)
            if char in '=<>!+-*/%&|^~':
                self.tokens.append(self.read_operator())
                continue
            
            # Unknown character
            self.tokens.append(Token(
                id=str(uuid.uuid4()),
                type=TokenType.UNKNOWN,
                value=char,
                position=self.position,
                line=self.line,
                column=self.column
            ))
            self.advance()
        
        # Add EOF token
        self.tokens.append(Token(
            id=str(uuid.uuid4()),
            type=TokenType.EOF,
            value='',
            position=self.position,
            line=self.line,
            column=self.column
        ))
        
        return self.tokens
    
    def reconstruct(self, tokens: List[Token]) -> str:
        """Reconstruct SQL from tokens"""
        return ''.join(token.value for token in tokens if token.type != TokenType.EOF)


if __name__ == "__main__":
    # Test multi-character operators
    test_queries = [
        "SELECT * FROM users WHERE id>=5",
        "SELECT * FROM users WHERE id<=10",
        "SELECT * FROM users WHERE id<>1",
        "SELECT * FROM users WHERE name!='admin'"
    ]
    
    print("Testing Multi-Character Operator Support")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        lexer = SQLLexer(query)
        tokens = lexer.tokenize()
        
        # Find operators
        operators = [t for t in tokens if t.type == TokenType.OPERATOR]
        print(f"Operators found: {[t.value for t in operators]}")
        
        # Test reconstruction
        reconstructed = lexer.reconstruct(tokens)
        print(f"Reconstructed: {reconstructed}")
        print(f"Match: {reconstructed == query}")
