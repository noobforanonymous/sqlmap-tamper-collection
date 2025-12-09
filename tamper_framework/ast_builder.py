#!/usr/bin/env python

"""
SQL AST (Abstract Syntax Tree) Builder

Builds a hierarchical representation of SQL structure.
This allows proper handling of:
- Nested subqueries
- Function calls
- Complex expressions
- Parenthesis nesting

Author: Regaan
License: GPL v2
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from tamper_framework.lexer import Token, TokenType


class NodeType(Enum):
    """AST node types"""
    ROOT = "ROOT"
    SELECT_STATEMENT = "SELECT_STATEMENT"
    SUBQUERY = "SUBQUERY"
    FUNCTION_CALL = "FUNCTION_CALL"
    EXPRESSION = "EXPRESSION"
    CLAUSE = "CLAUSE"
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    OPERATOR = "OPERATOR"
    KEYWORD = "KEYWORD"


@dataclass
class ASTNode:
    """
    Represents a node in the SQL Abstract Syntax Tree
    
    Each node has:
    - Type (what kind of SQL construct)
    - Tokens (the actual tokens that make up this node)
    - Children (nested nodes)
    - Parent (for traversal)
    """
    type: NodeType
    tokens: List[Token] = field(default_factory=list)
    children: List['ASTNode'] = field(default_factory=list)
    parent: Optional['ASTNode'] = None
    
    def add_child(self, child: 'ASTNode'):
        """Add a child node"""
        child.parent = self
        self.children.append(child)
    
    def get_depth(self) -> int:
        """Get nesting depth of this node"""
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth
    
    def is_subquery(self) -> bool:
        """Check if this node is a subquery"""
        return self.type == NodeType.SUBQUERY
    
    def __repr__(self):
        return f"ASTNode({self.type.value}, tokens={len(self.tokens)}, children={len(self.children)})"


class SQLASTBuilder:
    """
    Builds an Abstract Syntax Tree from SQL tokens
    
    This provides proper hierarchical structure:
    - SELECT statements
    - Nested subqueries
    - Function calls
    - Expressions
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.root = ASTNode(type=NodeType.ROOT)
    
    def current_token(self) -> Optional[Token]:
        """Get current token"""
        if self.position >= len(self.tokens):
            return None
        return self.tokens[self.position]
    
    def peek_token(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at token"""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return None
        return self.tokens[pos]
    
    def advance(self) -> Optional[Token]:
        """Move to next token"""
        token = self.current_token()
        self.position += 1
        return token
    
    def build(self) -> ASTNode:
        """
        Build the AST from tokens
        
        Returns the root node
        """
        while self.current_token() and self.current_token().type != TokenType.EOF:
            node = self._parse_statement()
            if node:
                self.root.add_child(node)
        
        return self.root
    
    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a SQL statement"""
        token = self.current_token()
        
        if not token or token.type == TokenType.EOF:
            return None
        
        # Check for SELECT statement
        if token.type == TokenType.KEYWORD and token.value.upper() == 'SELECT':
            return self._parse_select_statement()
        
        # For now, treat everything else as a clause
        return self._parse_clause()
    
    def _parse_select_statement(self) -> ASTNode:
        """Parse a SELECT statement"""
        node = ASTNode(type=NodeType.SELECT_STATEMENT)
        
        # Parse until we hit EOF or a semicolon
        while self.current_token() and self.current_token().type != TokenType.EOF:
            token = self.current_token()
            
            # Check for subquery (SELECT inside parentheses)
            if token.type == TokenType.LPAREN:
                subquery = self._parse_subquery()
                if subquery:
                    node.add_child(subquery)
                continue
            
            # Check for function call (identifier followed by lparen)
            if token.type == TokenType.IDENTIFIER and self.peek_token() and self.peek_token().type == TokenType.LPAREN:
                func = self._parse_function_call()
                if func:
                    node.add_child(func)
                continue
            
            # Add token to current node
            node.tokens.append(token)
            self.advance()
            
            # Stop at semicolon
            if token.type == TokenType.SEMICOLON:
                break
        
        return node
    
    def _parse_subquery(self) -> Optional[ASTNode]:
        """Parse a subquery (SELECT inside parentheses)"""
        # Consume opening paren
        lparen = self.advance()
        
        # Check if this is actually a subquery (contains SELECT)
        saved_pos = self.position
        is_subquery = False
        depth = 1
        
        while self.current_token() and depth > 0:
            token = self.current_token()
            
            if token.type == TokenType.LPAREN:
                depth += 1
            elif token.type == TokenType.RPAREN:
                depth -= 1
            elif token.type == TokenType.KEYWORD and token.value.upper() == 'SELECT':
                is_subquery = True
                break
            
            self.advance()
        
        # Restore position
        self.position = saved_pos
        
        if not is_subquery:
            # Not a subquery, just an expression in parentheses
            # Parse as expression
            return self._parse_expression()
        
        # Parse the subquery
        node = ASTNode(type=NodeType.SUBQUERY)
        node.tokens.append(lparen)
        
        # Parse SELECT statement inside
        select = self._parse_select_statement()
        if select:
            node.add_child(select)
        
        # Consume closing paren
        if self.current_token() and self.current_token().type == TokenType.RPAREN:
            node.tokens.append(self.advance())
        
        return node
    
    def _parse_function_call(self) -> ASTNode:
        """Parse a function call"""
        node = ASTNode(type=NodeType.FUNCTION_CALL)
        
        # Function name
        node.tokens.append(self.advance())
        
        # Opening paren
        if self.current_token() and self.current_token().type == TokenType.LPAREN:
            node.tokens.append(self.advance())
        
        # Parse arguments until closing paren
        depth = 1
        while self.current_token() and depth > 0:
            token = self.current_token()
            
            if token.type == TokenType.LPAREN:
                depth += 1
            elif token.type == TokenType.RPAREN:
                depth -= 1
                if depth == 0:
                    node.tokens.append(self.advance())
                    break
            
            node.tokens.append(self.advance())
        
        return node
    
    def _parse_expression(self) -> ASTNode:
        """Parse an expression in parentheses"""
        node = ASTNode(type=NodeType.EXPRESSION)
        
        # Opening paren
        if self.current_token() and self.current_token().type == TokenType.LPAREN:
            node.tokens.append(self.advance())
        
        # Parse until closing paren
        depth = 1
        while self.current_token() and depth > 0:
            token = self.current_token()
            
            if token.type == TokenType.LPAREN:
                depth += 1
            elif token.type == TokenType.RPAREN:
                depth -= 1
                if depth == 0:
                    node.tokens.append(self.advance())
                    break
            
            node.tokens.append(self.advance())
        
        return node
    
    def _parse_clause(self) -> ASTNode:
        """Parse a generic clause"""
        node = ASTNode(type=NodeType.CLAUSE)
        
        # Collect tokens until we hit a major keyword or EOF
        major_keywords = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'UNION', 'ORDER', 'GROUP', 'HAVING'}
        
        while self.current_token() and self.current_token().type != TokenType.EOF:
            token = self.current_token()
            
            # Stop at major keywords (except the first one)
            if len(node.tokens) > 0 and token.type == TokenType.KEYWORD and token.value.upper() in major_keywords:
                break
            
            node.tokens.append(token)
            self.advance()
        
        return node


def reconstruct_from_ast(node: ASTNode) -> str:
    """
    Reconstruct SQL from AST
    
    CRITICAL: Must maintain proper order of tokens and children
    Children represent nested structures that were parsed out
    """
    if not node.children:
        # Leaf node - just return tokens
        return ''.join(token.value for token in node.tokens)
    
    # Node has children - need to interleave properly
    # Strategy: Build a map of positions and reconstruct in order
    items = []
    
    # Add all tokens with their positions
    for token in node.tokens:
        items.append((token.position, token.value))
    
    # Add all children with their first token's position
    for child in node.children:
        if child.tokens:
            first_pos = child.tokens[0].position
            items.append((first_pos, reconstruct_from_ast(child)))
    
    # Sort by position and concatenate
    items.sort(key=lambda x: x[0])
    return ''.join(item[1] for item in items)


if __name__ == "__main__":
    from tamper_framework.lexer import SQLLexer
    
    # Test AST building
    test_queries = [
        "SELECT * FROM users WHERE id=1",
        "SELECT * FROM (SELECT id FROM users) AS sub",
        "SELECT COUNT(*) FROM users WHERE active=1",
    ]
    
    print("Testing AST Builder")
    print("=" * 70)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        
        # Tokenize
        lexer = SQLLexer(query)
        tokens = lexer.tokenize()
        
        # Build AST
        builder = SQLASTBuilder(tokens)
        ast = builder.build()
        
        # Show structure
        def print_tree(node, indent=0):
            print("  " * indent + str(node))
            for child in node.children:
                print_tree(child, indent + 1)
        
        print_tree(ast)
        
        # Reconstruct
        reconstructed = reconstruct_from_ast(ast)
        print(f"\nReconstructed: {reconstructed}")
        print(f"Match: {reconstructed == query}")
