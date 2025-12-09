# Contributing to SQL Tamper Framework

Thank you for your interest in contributing! This document provides guidelines for contributing to the SQL Tamper Framework.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- Framework version
- SQLMap version
- Detailed steps to reproduce
- Expected vs actual behavior
- SQL payload (sanitized)
- Target database type
- Logs/error messages

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Features

Feature suggestions are welcome! Please:

- Check existing feature requests first
- Clearly describe the problem and solution
- Provide examples and use cases
- Indicate if you can implement it

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Sharing WAF Bypasses

Have a new WAF bypass technique? Share it!

**Important:** Only share techniques discovered during **authorized testing**.

Use the [WAF Bypass template](.github/ISSUE_TEMPLATE/waf_bypass.md).

## Development Process

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/noobforanonymous/sqlmap-tamper-collection.git
cd sqlmap-tamper-collection

# Install in development mode
pip install -e .

# Run tests
python tests/test_lexer.py
python tests/test_transformer.py
python tests/test_integration.py
```

### Creating a Transformation Module

1. **Create the module** in `tamper_framework/transformations/`

```python
from tamper_framework.lexer import Token, TokenType
from tamper_framework.transformer import TransformationRule
from tamper_framework.context import SQLContext

def create_my_transform_rule() -> TransformationRule:
    """
    Create your transformation rule
    """
    
    def my_transform(token: Token, context: SQLContext) -> Token:
        # Your transformation logic
        return Token(
            id=token.id,  # Keep UUID
            type=token.type,
            value=new_value,
            position=token.position,
            line=token.line,
            column=token.column
        )
    
    return TransformationRule(
        name="my_transform",
        transform_func=my_transform,
        target_types=[TokenType.KEYWORD],
        skip_types=[TokenType.STRING_LITERAL, TokenType.COMMENT],
        track_transformed=True
    )
```

2. **Add to `__init__.py`**

```python
from tamper_framework.transformations.my_transform import create_my_transform_rule

__all__ = [
    # ... existing
    'create_my_transform_rule',
]
```

3. **Write tests**

Create `tests/test_my_transform.py`:

```python
from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import create_my_transform_rule

def test_my_transform():
    transformer = SQLTransformer()
    transformer.add_rule(create_my_transform_rule())
    
    result = transformer.transform("SELECT * FROM users")
    assert result != "SELECT * FROM users"
    # Add specific assertions
```

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   # Run all tests
   python tests/test_lexer.py
   python tests/test_transformer.py
   python tests/test_integration.py
   
   # Test with SQLMap
   sqlmap -u "http://target.com?id=1" --tamper=your_script
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create Pull Request**
   - Describe your changes
   - Reference related issues
   - Include test results

### Commit Message Guidelines

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement

**Example:**
```
feat: Add PostgreSQL operator encoding

- Implement PostgreSQL-specific operators
- Add context-aware encoding
- Include tests for all operators

Closes #123
```

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

**Example:**
```python
def transform_token(token: Token, context: SQLContext) -> Token:
    """
    Transform a token based on context
    
    Args:
        token: Token to transform
        context: SQL context information
        
    Returns:
        Transformed token
    """
    # Implementation
```

### Critical Rules

1. **Always preserve token.id (UUID)**
   ```python
   # CORRECT
   return Token(id=token.id, ...)
   
   # WRONG
   return Token(id=str(uuid.uuid4()), ...)
   ```

2. **Handle multi-character operators correctly**
   ```python
   # CORRECT
   if operator == '>=':
       return '%3E%3D'
   
   # WRONG
   for char in operator:
       encode(char)  # Breaks >=
   ```

3. **Check SQL context**
   ```python
   # CORRECT
   if context.clause == ClauseType.WHERE:
       # Transform
   
   # WRONG
   # Transform everywhere
   ```

## Testing

### Running Tests

```bash
# All tests
python tests/test_lexer.py
python tests/test_transformer.py
python tests/test_integration.py

# Specific test
python -m pytest tests/test_lexer.py::test_multi_char_operators
```

### Writing Tests

```python
def test_feature():
    """Test description"""
    # Setup
    transformer = SQLTransformer()
    transformer.add_rule(create_rule())
    
    # Execute
    result = transformer.transform(query)
    
    # Assert
    assert expected in result
    assert result != query
```

## Documentation

### Update Documentation

When adding features, update:
- `README.md` - User-facing documentation
- `docs/API.md` - API reference
- `docs/ARCHITECTURE.md` - Architecture details
- Docstrings in code

### Documentation Style

- Clear and concise
- Include examples
- Explain why, not just what
- Keep it up to date

## Responsible Disclosure

### Security Vulnerabilities

**Do NOT open public issues for security vulnerabilities.**

Email: security@rothackers.com

### WAF Bypasses

When sharing WAF bypasses:
- ✅ Only share authorized discoveries
- ✅ Sanitize sensitive information
- ✅ Provide context and testing details
- ❌ Don't share zero-days publicly
- ❌ Don't include client information

## Getting Help

- **Questions:** Use [Discussions](https://github.com/noobforanonymous/sqlmap-tamper-collection/discussions)
- **Bugs:** Use [Issues](https://github.com/noobforanonymous/sqlmap-tamper-collection/issues)
- **Email:** support@rothackers.com

## Recognition

Contributors are recognized in:
- Release notes
- README.md contributors section
- Git commit history

Thank you for contributing to the SQL Tamper Framework! 🚀
