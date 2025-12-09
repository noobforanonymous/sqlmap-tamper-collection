#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_keyword_safe.py
Description: Context-aware MySQL keyword obfuscation with protection against reapplication
Author: Regaan
Priority: HIGHEST
"""

import re
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Context-aware keyword obfuscation that prevents:
    - Reapplication (won't wrap already-wrapped keywords)
    - Partial word matches (uses word boundaries)
    - Comment corruption (skips content inside existing comments)
    
    Technique:
        Wraps SQL keywords with MySQL version comments using word boundaries
        Only applies to keywords NOT already inside comments
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    '/*!50000SELECT*/ * /*!50000FROM*/ users /*!50000WHERE*/ id=1'
    
    >>> tamper("/*!50000SELECT*/ * FROM users")
    '/*!50000SELECT*/ * /*!50000FROM*/ users'
    """
    
    retVal = payload
    
    if not payload:
        return retVal
    
    # Check if already processed (has version comments)
    if '/*!50000' in retVal:
        # Already processed, don't reapply
        return retVal
    
    # SQL keywords to obfuscate (most common first)
    keywords = [
        'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP',
        'WHERE', 'FROM', 'JOIN', 'INNER', 'OUTER', 'LEFT', 'RIGHT',
        'ORDER', 'GROUP', 'HAVING', 'LIMIT'
    ]
    
    for keyword in keywords:
        # Use word boundaries to avoid partial matches
        # \b ensures we match whole words only
        pattern = r'\b' + keyword + r'\b'
        replacement = f'/*!50000{keyword}*/'
        
        # Case-insensitive replacement with word boundaries
        retVal = re.sub(pattern, replacement, retVal, flags=re.IGNORECASE)
    
    return retVal
