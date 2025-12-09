# SQL Tamper Framework Architecture

## Overview

This framework provides token-based and AST-based SQL transformation for WAF bypass with proper safeguards.

## Core Components

### 1. Lexer (`tamper_framework/lexer.py`)

**Purpose:** Tokenizes SQL queries into structured tokens

**Key Features:**
- UUID-based token tracking (prevents position bugs)
- Multi-character operator support (`>=`, `<=`, `<>`, `!=`)
- String literal handling with escape sequences
- Comment preservation (block and line)
- Position and line tracking

**Token Types:**
- `KEYWORD` - SQL keywords (SELECT, FROM, WHERE, etc.)
- `IDENTIFIER` - Table/column names
- `STRING_LITERAL` - String values with quotes
- `NUMBER` - Numeric literals
- `OPERATOR` - Comparison and arithmetic operators
- `WHITESPACE` - Spaces, tabs, newlines
- `COMMENT` - SQL comments
- `LPAREN/RPAREN` - Parentheses
- `COMMA`, `SEMICOLON`, `DOT` - Delimiters

**Example:**
```python
from tamper_framework.lexer import SQLLexer

lexer = SQLLexer("SELECT * FROM users WHERE id>=5")
tokens = lexer.tokenize()

# Each token has:
# - id: UUID for tracking
# - type: TokenType enum
# - value: Original text
# - position: Character position
# - line, column: Location tracking
```

### 2. Context Tracker (`tamper_framework/context.py`)

**Purpose:** Tracks SQL clause state and nesting

**Key Features:**
- Knows current clause (SELECT, WHERE, FROM, etc.)
- Tracks nesting depth (subqueries)
- Detects function calls
- Parent/child context relationships

**Clause Types:**
- `SELECT`, `FROM`, `WHERE`, `JOIN`, `ON`
- `GROUP_BY`, `HAVING`, `ORDER_BY`, `LIMIT`
- `INSERT`, `UPDATE`, `DELETE`, `VALUES`, `SET`
- `UNION`

**Example:**
```python
from tamper_framework.context import annotate_tokens_with_context

tokens = lexer.tokenize()
annotated = annotate_tokens_with_context(tokens)

for token, context in annotated:
    print(f"{token.value} -> {context.clause}, depth={context.depth}")
```

### 3. Token Transformer (`tamper_framework/transformer.py`)

**Purpose:** Context-aware token transformation

**Key Features:**
- UUID-based tracking (no position bugs)
- SQL context filtering (only transform in specific clauses)
- Reapplication protection
- Deterministic output

**Transformation Rules:**
- `target_types`: Which token types to transform
- `skip_types`: Which types to skip (strings, comments)
- `allowed_clauses`: Only transform in these clauses
- `track_transformed`: Prevent reapplication

**Example:**
```python
from tamper_framework.transformer import SQLTransformer, TransformationRule

def my_transform(token, context):
    # Only transform in WHERE clause
    if context.clause == ClauseType.WHERE:
        return modified_token
    return token

rule = TransformationRule(
    name="my_rule",
    transform_func=my_transform,
    target_types=[TokenType.OPERATOR],
    allowed_clauses=[ClauseType.WHERE]
)

transformer = SQLTransformer()
transformer.add_rule(rule)
result = transformer.transform(sql)
```

### 4. AST Builder (`tamper_framework/ast_builder.py`)

**Purpose:** Builds hierarchical SQL structure

**Key Features:**
- Detects nested subqueries
- Identifies function calls
- Tracks expression nesting
- Proper reconstruction

**Node Types:**
- `ROOT` - Top-level container
- `SELECT_STATEMENT` - SELECT query
- `SUBQUERY` - Nested SELECT
- `FUNCTION_CALL` - SQL function
- `EXPRESSION` - Parenthesized expression
- `CLAUSE` - Generic clause

**Example:**
```python
from tamper_framework.ast_builder import SQLASTBuilder

builder = SQLASTBuilder(tokens)
ast = builder.build()

# AST structure:
# ROOT
#   SELECT_STATEMENT
#     SUBQUERY (if nested)
#       SELECT_STATEMENT
```

### 5. AST Transformer (`tamper_framework/ast_transformer.py`)

**Purpose:** Structure-aware transformation

**Key Features:**
- Transform based on node type
- Depth-aware (only transform at certain nesting levels)
- Parent/child awareness

**Example:**
```python
from tamper_framework.ast_transformer import ASTTransformer, ASTTransformationRule

# Only transform top-level SELECT (not subqueries)
rule = ASTTransformationRule(
    name="top_level_only",
    transform_func=my_func,
    target_token_types=[TokenType.KEYWORD],
    target_node_types=[NodeType.SELECT_STATEMENT],
    max_depth=1  # Only depth 1
)
```

## Transformation Modules

### Keyword Wrap (`transformations/keyword_wrap.py`)

Wraps SQL keywords in MySQL version comments.

```
SELECT -> /*!50000SELECT*/
```

### Space Replace (`transformations/space_replace.py`)

Replaces spaces with inline comments.

```
' ' -> '/**/'
```

### Case Alternate (`transformations/case_alternate.py`)

Applies alternating case to keywords.

```
SELECT -> sElEcT
```

### Value Encode (`transformations/value_encode.py`)

URL encodes operators in WHERE/HAVING clauses.

**CRITICAL FIX:** Encodes complete operators
```
>= -> %3E%3D (correct)
NOT: >= -> %3E= (broken)
```

## Design Decisions

### Why UUID Tracking?

**Problem:** Position-based tracking breaks when token values change length.

```python
# Token at position 10: "SELECT"
# After wrapping: "/*!50000SELECT*/"
# Position 10 is now invalid!
```

**Solution:** Each token gets a UUID that never changes.

### Why Context Awareness?

**Problem:** Can't tell if `=` is in SELECT or WHERE clause.

```sql
SELECT * FROM users WHERE id=1
       ^                    ^
    (don't encode)      (encode this)
```

**Solution:** Track SQL clause state.

### Why Multi-Char Operator Support?

**Problem:** Naive lexing breaks `>=` into `>` and `=`.

```python
# WRONG:
'>=' -> '>' + '=' -> encode to '%3E' + '='
Result: '%3E=' (broken SQL!)

# RIGHT:
'>=' -> '%3E%3D' (complete encoding)
```

**Solution:** Check multi-char operators FIRST in lexer.

## Testing Strategy

### Unit Tests
- `test_lexer.py` - Lexer functionality
- `test_transformer.py` - Transformation rules

### Integration Tests
- `test_integration.py` - Real SQLMap payloads

**All 32 tests passing!**

## Performance Considerations

**Token-based vs AST-based:**
- Token-based: Faster, simpler
- AST-based: More accurate, handles nesting

**Use token-based for:**
- Simple transformations
- Clause-aware operations

**Use AST-based for:**
- Nested query handling
- Depth-aware transformations

## Known Limitations

1. **MySQL/MariaDB Focus**
   - Designed for MySQL syntax
   - May not work with PostgreSQL, MSSQL, Oracle

2. **Simplified Parsing**
   - Not a full SQL parser
   - Complex edge cases may fail

3. **WAF Dependent**
   - Effectiveness varies by WAF
   - No universal guarantee

## Future Enhancements

1. **Full SQL Parser**
   - Complete AST for all SQL constructs
   - Better error handling

2. **Multi-Database Support**
   - PostgreSQL syntax
   - MSSQL syntax
   - Oracle syntax

3. **Advanced Transformations**
   - Encoding variations
   - Character set manipulation
   - Unicode obfuscation
