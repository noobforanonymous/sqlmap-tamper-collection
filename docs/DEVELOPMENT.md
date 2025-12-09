# Development Guide

## Setting Up Development Environment

### Requirements
- Python 3.7+
- No external dependencies (pure Python)

### Installation

```bash
git clone https://github.com/noobforanonymous/sqlmap-tamper-collection.git
cd sqlmap-tamper-collection

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
python3 tests/test_lexer.py
python3 tests/test_transformer.py
python3 tests/test_integration.py

# Or run individually
cd tests
python3 test_lexer.py
```

## Project Structure

```
sqlmap-tamper-collection/
├── tamper_framework/          # Core framework
│   ├── __init__.py
│   ├── __version__.py
│   ├── lexer.py              # SQL tokenizer
│   ├── context.py            # Context tracker
│   ├── transformer.py        # Token transformer
│   ├── ast_builder.py        # AST builder
│   ├── ast_transformer.py    # AST transformer
│   └── transformations/      # Transformation modules
│       ├── __init__.py
│       ├── keyword_wrap.py
│       ├── space_replace.py
│       ├── case_alternate.py
│       └── value_encode.py
├── tamper_scripts/           # SQLMap tamper scripts
│   └── cloudflare2025.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_lexer.py
│   ├── test_transformer.py
│   └── test_integration.py
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEVELOPMENT.md
├── README.md
├── setup.py
└── requirements.txt
```

## Creating a New Transformation

### Step 1: Create Transformation Module

Create `tamper_framework/transformations/my_transform.py`:

```python
from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext

def create_my_transform_rule() -> TransformationRule:
    """
    Create your transformation rule
    """
    
    def my_transform(token: Token, context: SQLContext) -> Token:
        """Transform function"""
        if token.type == TokenType.KEYWORD:
            # Modify token
            new_value = transform_value(token.value)
            return Token(
                id=token.id,  # Keep same UUID
                type=token.type,
                value=new_value,
                position=token.position,
                line=token.line,
                column=token.column
            )
        return token
    
    return TransformationRule(
        name="my_transform",
        transform_func=my_transform,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True
    )
```

### Step 2: Add to __init__.py

Edit `tamper_framework/transformations/__init__.py`:

```python
from tamper_framework.transformations.my_transform import create_my_transform_rule

__all__ = [
    # ... existing
    'create_my_transform_rule',
]
```

### Step 3: Test Your Transformation

Create `tests/test_my_transform.py`:

```python
from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import create_my_transform_rule

def test_my_transform():
    transformer = SQLTransformer()
    transformer.add_rule(create_my_transform_rule())
    
    query = "SELECT * FROM users"
    result = transformer.transform(query)
    
    assert result != query
    # Add your assertions
    print("✓ test_my_transform passed")

if __name__ == "__main__":
    test_my_transform()
```

## Debugging Tips

### Enable Verbose Output

```python
from tamper_framework.lexer import SQLLexer

lexer = SQLLexer(query)
tokens = lexer.tokenize()

# Print all tokens
for token in tokens:
    print(token)
```

### Check Context

```python
from tamper_framework.context import annotate_tokens_with_context

annotated = annotate_tokens_with_context(tokens)
for token, context in annotated:
    print(f"{token.value} -> {context}")
```

### Visualize AST

```python
from tamper_framework.ast_builder import SQLASTBuilder

builder = SQLASTBuilder(tokens)
ast = builder.build()

def print_tree(node, indent=0):
    print("  " * indent + str(node))
    for child in node.children:
        print_tree(child, indent + 1)

print_tree(ast)
```

## Common Pitfalls

### 1. Modifying Token Position

**WRONG:**
```python
return Token(
    id=token.id,
    type=token.type,
    value=new_value,
    position=new_position,  # Don't change position!
    line=token.line,
    column=token.column
)
```

**RIGHT:**
```python
return Token(
    id=token.id,
    type=token.type,
    value=new_value,
    position=token.position,  # Keep original
    line=token.line,
    column=token.column
)
```

### 2. Breaking Multi-Char Operators

**WRONG:**
```python
# Encoding each character separately
for char in operator:
    encode(char)
```

**RIGHT:**
```python
# Encode complete operator
if operator == '>=':
    return '%3E%3D'
```

### 3. Not Checking Context

**WRONG:**
```python
# Encoding all operators everywhere
if token.type == TokenType.OPERATOR:
    return encode(token)
```

**RIGHT:**
```python
# Only encode in WHERE clause
if token.type == TokenType.OPERATOR and context.clause == ClauseType.WHERE:
    return encode(token)
```

## Code Style

### Follow These Guidelines:

1. **Use type hints**
```python
def transform(token: Token, context: SQLContext) -> Token:
    pass
```

2. **Document functions**
```python
def my_function():
    """
    Brief description
    
    Detailed explanation if needed
    """
    pass
```

3. **Keep UUID intact**
```python
# Always preserve token.id
new_token = Token(id=token.id, ...)
```

4. **Handle edge cases**
```python
if not payload:
    return payload

try:
    result = transform(payload)
except Exception:
    return payload  # Fail safe
```

## Contributing

### Before Submitting:

1. **Run all tests**
```bash
python3 tests/test_lexer.py
python3 tests/test_transformer.py
python3 tests/test_integration.py
```

2. **Test with real SQLMap**
```bash
sqlmap -u "http://target.com?id=1" --tamper=cloudflare2025
```

3. **Document changes**
- Update API.md if adding new functions
- Update ARCHITECTURE.md if changing design
- Add tests for new features

## Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in __version__.py
- [ ] Tested with SQLMap
- [ ] No debug code left
- [ ] README.md updated
