# SQLMap Tamper Scripts Collection

Context-aware WAF bypass tamper scripts for SQLMap with proper safeguards.

**Author:** Regaan  
**Created:** December 2025  
**License:** GPL v2 (SQLMap compatible)

---

## Design Philosophy

These tamper scripts are built with engineering discipline:

- **Deterministic** - Same input produces same output
- **Context-aware** - Understands SQL structure
- **Safe chaining** - Won't break when combined
- **Reapplication-protected** - Won't corrupt already-transformed payloads
- **Word-boundary aware** - No partial keyword matches
- **String-preserving** - Maintains literal integrity

---

## Critical Limitations

**IMPORTANT - READ BEFORE USE**

These scripts have known limitations:

1. **MySQL-specific** - Designed for MySQL/MariaDB backends
2. **Not universal** - May break with PostgreSQL, MSSQL, Oracle
3. **Simplified parsing** - Not a full SQL parser
4. **WAF-dependent** - Effectiveness varies by WAF configuration
5. **No guarantees** - Success depends on target environment

**Do NOT expect these to bypass every WAF.**

---

## Installation

```bash
git clone https://github.com/noobforanonymous/sqlmap-tamper-collection.git
cd sqlmap-tamper-collection
cp *.py /path/to/sqlmap/tamper/
```

---

## Tamper Scripts

### cloudflare_keyword.py

**Purpose:** Wrap SQL keywords in MySQL version comments

**Technique:**
```sql
SELECT → /*!50000SELECT*/
```

**Safeguards:**
- Reapplication protection (won't double-wrap)
- Word boundaries (no partial matches like INNER_JOIN)
- Case-insensitive matching

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_keyword
```

**Limitations:**
- MySQL/MariaDB only
- May break with complex nested queries

---

### cloudflare_space.py

**Purpose:** Replace spaces with inline comments

**Technique:**
```sql
SELECT * FROM → SELECT/**/*/**/FROM
```

**Safeguards:**
- Preserves string literals
- Won't replace spaces inside quotes
- Reapplication protection

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_space
```

**Limitations:**
- May break with non-MySQL databases
- Simplified string detection

---

### cloudflare_case.py

**Purpose:** Apply alternating case to SQL keywords

**Technique:**
```sql
SELECT → sElEcT
```

**Safeguards:**
- Word boundaries (whole words only)
- Reapplication protection
- Preserves string literals

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_case
```

**Limitations:**
- Only affects known keywords
- May miss custom SQL functions

---

### cloudflare_encode.py

**Purpose:** Context-aware URL encoding

**Technique:**
```sql
WHERE id=1 → WHERE id%3D1
```

**Safeguards:**
- Only encodes in value context
- Preserves SQL structure
- Won't break comments

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_encode
```

**Limitations:**
- Simplified context detection
- May miss complex expressions

---

### cloudflare2025.py

**Purpose:** Combined multi-layer bypass with all safeguards

**Technique Stack:**
1. Keyword wrapping (with protection)
2. Space replacement (context-aware)
3. Value encoding (safe contexts only)
4. Case variation (keywords only)

**Example:**
```
Input:  SELECT * FROM users WHERE id=1
Output: /*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3D1
```

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare2025
```

**IMPORTANT:** Use this script STANDALONE. Do NOT chain with other cloudflare_* scripts.

**Limitations:**
- MySQL/MariaDB only
- Complex queries may break
- Not tested with all SQL dialects

---

## Chaining Guidelines

**RECOMMENDED:**

Use `cloudflare2025.py` standalone:
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare2025
```

**NOT RECOMMENDED:**

Chaining individual scripts may cause conflicts:
```bash
# DON'T DO THIS
sqlmap -u "https://target.com?id=1" \
  --tamper=cloudflare_keyword,cloudflare_space,cloudflare_case
```

**Why?** The combined script already includes all transformations in the correct order with proper safeguards.

---

## Testing Methodology

### Environment
- Target: Custom vulnerable web application
- WAFs: Cloudflare, ModSecurity, AWS WAF
- SQLMap: 1.8+
- Database: MySQL 5.7+, MariaDB 10.x
- Test Date: December 2025

### Procedure
1. Baseline test without tamper (verify blocking)
2. Apply tamper script
3. Verify SQL still executes correctly
4. Confirm WAF bypass (if applicable)
5. Test for reapplication safety
6. Validate deterministic behavior

### Results

**cloudflare2025.py:**
- Successfully bypassed test WAF configurations
- Maintained SQL validity in test cases
- Deterministic output verified
- Reapplication-safe confirmed

**Individual scripts:**
- Each script tested independently
- Safeguards verified
- Edge cases documented

**Known Failures:**
- Complex nested subqueries
- Non-MySQL databases
- Highly restrictive WAF rules
- Queries with extensive string literals

---

## Advanced Usage

### Test Locally

```python
#!/usr/bin/env python3

import sys
sys.path.insert(0, '/path/to/sqlmap')

from tamper.cloudflare2025 import tamper

payload = "SELECT * FROM users WHERE id=1"
result = tamper(payload)

print(f"Original: {payload}")
print(f"Bypassed: {result}")

# Test deterministic
result2 = tamper(payload)
assert result == result2, "Not deterministic!"
print("Deterministic: PASS")
```

### With SQLMap Options

```bash
sqlmap -u "https://target.com?id=1" \
  --tamper=cloudflare2025 \
  --random-agent \
  --delay=2 \
  --level=5 \
  --risk=3 \
  --threads=1
```

---

## Known Issues

### Issue 1: Complex Nested Queries
**Problem:** Deeply nested subqueries may break  
**Workaround:** Simplify query structure or use individual tampers

### Issue 2: Non-MySQL Databases
**Problem:** Scripts designed for MySQL syntax  
**Workaround:** Modify for target database or use database-specific tampers

### Issue 3: String Literal Edge Cases
**Problem:** Escaped quotes may confuse parser  
**Workaround:** Test payload manually before automation

### Issue 4: Over-obfuscation
**Problem:** Some WAFs detect excessive obfuscation  
**Workaround:** Use individual tampers instead of combined

---

## Comparison with Random Tampers

| Feature | Random Tampers | These Scripts |
|---------|----------------|---------------|
| Reproducible | No | Yes |
| Debuggable | No | Yes |
| Testable | No | Yes |
| Context-aware | No | Yes |
| Reapplication-safe | No | Yes |
| String-preserving | No | Yes |

---

## Requirements

- SQLMap 1.8 or higher
- Python 2.7 or 3.x
- MySQL/MariaDB target (for best results)

---

## Contributing

Contributions welcome with these requirements:

**Code Quality:**
- Deterministic transformations only
- Context-aware parsing
- Reapplication protection
- Word boundary awareness
- String literal preservation

**Documentation:**
- Clear technique explanation
- Known limitations listed
- Test results included
- No exaggerated claims

**Testing:**
- Deterministic behavior verified
- Reapplication safety confirmed
- Edge cases documented
- Real-world validation

Submit pull requests with:
1. Tamper script code
2. Test results
3. Limitation documentation
4. Usage examples

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

**Legal Notice:**

Unauthorized access to computer systems is illegal under:
- Computer Fraud and Abuse Act (CFAA) - United States
- Computer Misuse Act - United Kingdom
- Similar laws in other jurisdictions

By using these tools, you agree to:
- Use them legally and responsibly
- Obtain proper authorization
- Accept full responsibility for your actions

The author (Regaan) is not responsible for misuse or damage caused by these tools.

---

## Credits

Inspired by the SQLMap project and security research community.

Built with engineering discipline and real-world testing.

---

## Support

- **GitHub Issues:** https://github.com/noobforanonymous/sqlmap-tamper-collection/issues
- **Documentation:** This README
- **Email:** support@rothackers.com

---

## Changelog

### v1.0.0 - December 2025
- Initial release
- Five tamper scripts with safeguards
- Context-aware transformations
- Reapplication protection
- Comprehensive documentation

---

**Built with engineering discipline, not marketing hype.**
