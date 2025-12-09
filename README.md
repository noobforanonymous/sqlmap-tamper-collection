# SQL Tamper Framework

Context-aware SQL transformation framework for WAF bypass with proper safeguards.

**Author:** Regaan  
**License:** GPL v2  
**Version:** 2.0.0

---

## Features

### Token-Based Transformation
- Full SQL lexer with UUID tracking
- Multi-character operator support (`>=`, `<=`, `<>`, `!=`)
- Context-aware transformations
- String literal and comment preservation

### AST-Based Transformation
- Hierarchical SQL structure
- Nested subquery handling
- Depth-aware transformations
- Function call detection

### Safety Guarantees
- Deterministic output (same input = same output)
- Reapplication protection
- SQL validity preservation
- No random mutations

---

## Installation

```bash
git clone https://github.com/noobforanonymous/sqlmap-tamper-collection.git
cd sqlmap-tamper-collection

# Copy tamper script to SQLMap
cp tamper_scripts/cloudflare2025.py /path/to/sqlmap/tamper/

# Or install framework for development
pip install -e .
```

---

## Quick Start

### With SQLMap

```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare2025
```

### Standalone Testing

```bash
cd tamper_scripts
python3 cloudflare2025.py
```

---

## Tamper Script

### cloudflare2025.py

Context-aware multi-layer WAF bypass.

**Transformations:**

1. **Keyword Wrapping** - MySQL version comments
   ```sql
   SELECT -> /*!50000SELECT*/
   ```

2. **Space Replacement** - Inline comments
   ```sql
   ' ' -> '/**/'
   ```

3. **Value Encoding** - URL encoding (WHERE/HAVING only)
   ```sql
   >= -> %3E%3D
   ```

4. **Case Alternation** - Alternating case
   ```sql
   SELECT -> sElEcT
   ```

**Example:**
```
Input:  SELECT * FROM users WHERE id>=5
Output: /*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3E%3D5
```

**Critical Fixes:**
- Operators encoded correctly (`>=` becomes `%3E%3D`, not `%3E=`)
- UUID tracking prevents position bugs
- Context-aware (only encodes in WHERE/HAVING)
- Deterministic output
- String/comment preservation

---

## Framework Architecture

### Core Components

**Lexer** (`tamper_framework/lexer.py`)
- Tokenizes SQL queries
- UUID-based token tracking
- Multi-char operator support

**Context Tracker** (`tamper_framework/context.py`)
- Tracks SQL clause state
- Knows WHERE vs SELECT vs FROM
- Nesting depth tracking

**Transformer** (`tamper_framework/transformer.py`)
- Context-aware transformations
- Reapplication protection
- Deterministic output

**AST Builder** (`tamper_framework/ast_builder.py`)
- Hierarchical SQL structure
- Subquery detection
- Function call handling

### Transformation Modules

- `keyword_wrap.py` - Keyword obfuscation
- `space_replace.py` - Space replacement
- `case_alternate.py` - Case variation
- `value_encode.py` - Value encoding

---

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
from tamper_framework.transformations import create_value_encode_rule

transformer = SQLTransformer()
transformer.add_rule(create_value_encode_rule())

# Only encodes in WHERE clause
result = transformer.transform("SELECT * FROM users WHERE id>=5")
# WHERE clause: id%3E%3D5
# SELECT clause: * (not encoded)
```

### Custom Transformation

```python
from tamper_framework.transformer import TransformationRule
from tamper_framework.lexer import Token, TokenType
from tamper_framework.context import SQLContext, ClauseType

def my_transform(token: Token, context: SQLContext) -> Token:
    if context.clause == ClauseType.WHERE:
        # Transform only in WHERE clause
        pass
    return token

rule = TransformationRule(
    name="my_rule",
    transform_func=my_transform,
    target_types=[TokenType.OPERATOR],
    allowed_clauses=[ClauseType.WHERE]
)
```

---

## Testing

### Run Tests

```bash
# All tests
python3 tests/test_lexer.py          # 9 tests
python3 tests/test_transformer.py    # 10 tests
python3 tests/test_integration.py    # 13 tests

# Total: 32/32 tests passing
```

### Test Results

- **Lexer Tests:** Multi-char operators, string literals, comments, UUID tracking
- **Transformer Tests:** All transformations, context awareness, deterministic output
- **Integration Tests:** Real SQLMap payloads, complex queries, edge cases

---

## Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - Framework design and components
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and best practices

---

## Technical Details

### Critical Fixes

**1. Multi-Character Operator Support**

Problem: Naive lexing breaks `>=` into `>` and `=`
```python
# WRONG: '>=' -> '%3E' + '=' = '%3E=' (broken SQL)
# RIGHT: '>=' -> '%3E%3D' (complete encoding)
```

Solution: Check multi-char operators FIRST in lexer

**2. UUID-Based Token Tracking**

Problem: Position-based tracking breaks when token values change
```python
# Token at position 10: "SELECT"
# After wrapping: "/*!50000SELECT*/"
# Position 10 is now invalid!
```

Solution: Each token gets a UUID that never changes

**3. Context Awareness**

Problem: Can't tell if operator is in SELECT or WHERE
```sql
SELECT * FROM users WHERE id=1
       ^                    ^
   (don't encode)      (encode this)
```

Solution: Track SQL clause state

---

## Known Limitations

### Current Scope

1. **MySQL/MariaDB Focus**
   - Designed for MySQL syntax
   - May not work with PostgreSQL, MSSQL, Oracle

2. **Simplified Parsing**
   - Not a full SQL parser
   - Complex nested queries may have edge cases

3. **WAF Dependent**
   - Effectiveness varies by WAF configuration
   - No universal bypass guarantee

### Edge Cases

**Complex Nested Queries:**
- Deeply nested subqueries may fail
- Workaround: Simplify query structure

**Non-MySQL Databases:**
- Scripts designed for MySQL syntax
- Workaround: Modify for target database

---

## Performance

**Token-Based vs AST-Based:**
- Token-based: Faster, simpler (use for most cases)
- AST-based: More accurate, handles nesting (use for complex queries)

**Benchmarks:**
- Simple query (10 tokens): ~1ms
- Complex query (100 tokens): ~5ms
- Nested subquery: ~10ms

---

## Contributing

Contributions welcome! Please:

1. **Run all tests** before submitting
2. **Document changes** in code and docs
3. **Follow code style** (see DEVELOPMENT.md)
4. **Test with real SQLMap** if possible

---

## Legal Disclaimer

**AUTHORIZED TESTING ONLY**

These tools are for authorized security testing only.

**Permitted Use:**
- Systems you own
- With written authorization
- Authorized penetration testing
- Bug bounty programs (within scope)

**Prohibited Use:**
- Unauthorized systems
- Illegal activities
- Causing harm or damage
- Violating terms of service

Unauthorized access to computer systems is illegal under:
- Computer Fraud and Abuse Act (CFAA) - United States
- Computer Misuse Act - United Kingdom
- Similar laws in other jurisdictions

By using these tools, you agree to use them legally and responsibly.

The author (Regaan) is not responsible for misuse or damage caused by these tools.

---

## Support

- **GitHub Issues:** https://github.com/noobforanonymous/sqlmap-tamper-collection/issues
- **Documentation:** See `docs/` directory
- **Email:** support@rothackers.com

---

## Changelog

### v2.0.0 - December 2025
- Complete rewrite with token-based framework
- UUID tracking for proper token management
- Multi-character operator support
- Context-aware transformations
- AST builder for hierarchical structure
- Comprehensive test suite (32 tests)
- Fixed operator encoding bug
- Deterministic output
- Reapplication protection

---

**Built with engineering discipline, tested thoroughly, documented completely.**
