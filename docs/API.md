# API Reference

## Lexer API

### SQLLexer

```python
class SQLLexer:
    def __init__(self, sql: str)
    def tokenize(self) -> List[Token]
    def reconstruct(self, tokens: List[Token]) -> str
```

**Methods:**
- `tokenize()` - Convert SQL to tokens
- `reconstruct()` - Convert tokens back to SQL

### Token

```python
@dataclass
class Token:
    id: str              # UUID
    type: TokenType      # Token type enum
    value: str           # Original text
    position: int        # Character position
    line: int           # Line number
    column: int         # Column number
```

## Context API

### SQLContext

```python
@dataclass
class SQLContext:
    clause: ClauseType
    depth: int
    in_function: bool
    in_subquery: bool
    parent: Optional[SQLContext]
```

### SQLContextTracker

```python
class SQLContextTracker:
    def process_token(self, token: Token) -> SQLContext
    def is_in_where_clause(self) -> bool
    def is_in_select_clause(self) -> bool
    def get_depth(self) -> int
```

### Helper Functions

```python
def annotate_tokens_with_context(tokens: List[Token]) -> List[tuple[Token, SQLContext]]
```

## Transformer API

### TransformationRule

```python
class TransformationRule:
    def __init__(
        self,
        name: str,
        transform_func: Callable[[Token, SQLContext], Token],
        target_types: List[TokenType],
        skip_types: List[TokenType] = None,
        allowed_clauses: List[ClauseType] = None,
        track_transformed: bool = True
    )
```

**Parameters:**
- `name` - Rule identifier
- `transform_func` - Function that transforms tokens
- `target_types` - Which token types to transform
- `skip_types` - Which types to skip (default: strings, comments)
- `allowed_clauses` - Only transform in these clauses
- `track_transformed` - Prevent reapplication

### SQLTransformer

```python
class SQLTransformer:
    def add_rule(self, rule: TransformationRule)
    def transform(self, sql: str) -> str
```

## AST API

### ASTNode

```python
@dataclass
class ASTNode:
    type: NodeType
    tokens: List[Token]
    children: List[ASTNode]
    parent: Optional[ASTNode]
    
    def add_child(self, child: ASTNode)
    def get_depth(self) -> int
    def is_subquery(self) -> bool
```

### SQLASTBuilder

```python
class SQLASTBuilder:
    def __init__(self, tokens: List[Token])
    def build(self) -> ASTNode
```

### Helper Functions

```python
def reconstruct_from_ast(node: ASTNode) -> str
```

## Transformation Modules

### create_keyword_wrap_rule()

```python
def create_keyword_wrap_rule() -> TransformationRule
```

Wraps keywords in MySQL version comments.

**Example:**
```python
transformer.add_rule(create_keyword_wrap_rule())
# SELECT -> /*!50000SELECT*/
```

### create_space_replace_rule()

```python
def create_space_replace_rule() -> TransformationRule
```

Replaces spaces with inline comments.

**Example:**
```python
transformer.add_rule(create_space_replace_rule())
# ' ' -> '/**/'
```

### create_case_alternate_rule()

```python
def create_case_alternate_rule() -> TransformationRule
```

Applies alternating case to keywords.

**Example:**
```python
transformer.add_rule(create_case_alternate_rule())
# SELECT -> sElEcT
```

### create_value_encode_rule()

```python
def create_value_encode_rule() -> TransformationRule
```

URL encodes operators in WHERE/HAVING clauses.

**Example:**
```python
transformer.add_rule(create_value_encode_rule())
# >= -> %3E%3D (in WHERE clause)
```

## Usage Examples

### Basic Transformation

```python
from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import create_keyword_wrap_rule

transformer = SQLTransformer()
transformer.add_rule(create_keyword_wrap_rule())

result = transformer.transform("SELECT * FROM users")
# Result: /*!50000SELECT*/ * /*!50000FROM*/ users
```

### Context-Aware Transformation

```python
from tamper_framework.transformer import SQLTransformer, TransformationRule
from tamper_framework.lexer import Token, TokenType
from tamper_framework.context import SQLContext, ClauseType

def encode_in_where(token: Token, context: SQLContext) -> Token:
    if context.clause == ClauseType.WHERE and token.value == '=':
        return Token(
            id=token.id,
            type=token.type,
            value='%3D',
            position=token.position,
            line=token.line,
            column=token.column
        )
    return token

rule = TransformationRule(
    name="where_encode",
    transform_func=encode_in_where,
    target_types=[TokenType.OPERATOR],
    allowed_clauses=[ClauseType.WHERE]
)

transformer = SQLTransformer()
transformer.add_rule(rule)
```

### AST-Based Transformation

```python
from tamper_framework.ast_transformer import ASTTransformer, ASTTransformationRule
from tamper_framework.ast_builder import NodeType

def transform_top_level(token: Token, node: ASTNode) -> Token:
    # Only transform at depth 1
    if node.get_depth() == 1:
        # Transform token
        pass
    return token

rule = ASTTransformationRule(
    name="top_level",
    transform_func=transform_top_level,
    target_token_types=[TokenType.KEYWORD],
    max_depth=1
)

transformer = ASTTransformer()
transformer.add_rule(rule)
```

### Custom Tamper Script

```python
from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import (
    create_keyword_wrap_rule,
    create_space_replace_rule,
    create_value_encode_rule,
    create_case_alternate_rule
)

def tamper(payload, **kwargs):
    if not payload:
        return payload
    
    transformer = SQLTransformer()
    transformer.add_rule(create_keyword_wrap_rule())
    transformer.add_rule(create_space_replace_rule())
    transformer.add_rule(create_value_encode_rule())
    transformer.add_rule(create_case_alternate_rule())
    
    try:
        return transformer.transform(payload)
    except Exception:
        return payload
```
