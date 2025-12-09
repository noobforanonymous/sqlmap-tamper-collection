#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_case_safe.py
Description: Context-aware case variation that only affects keywords
Author: Regaan
Priority: LOWEST
"""

import re
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOWEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Context-aware case variation that:
    - Only applies to SQL keywords
    - Preserves case in string literals
    - Won't reapply to already-alternated keywords
    - Uses word boundaries to avoid partial matches
    
    Technique:
        Applies alternating case ONLY to SQL keywords
        Pattern: sElEcT (lowercase, uppercase, lowercase, uppercase...)
        
        Does NOT affect:
        - String literals
        - Table/column names
        - Already-alternated keywords
    
    >>> tamper("SELECT * FROM users")
    'sElEcT * fRoM users'
    
    >>> tamper("sElEcT * FROM users")
    'sElEcT * fRoM users'
    """
    
    retVal = payload
    
    if not payload:
        return retVal
    
    # SQL keywords to apply alternating case
    keywords = [
        'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE',
        'WHERE', 'FROM', 'JOIN', 'ORDER', 'GROUP', 'HAVING'
    ]
    
    for keyword in keywords:
        # Create alternating case version
        alternating = ''.join(
            char.lower() if i % 2 == 0 else char.upper()
            for i, char in enumerate(keyword)
        )
        
        # Check if keyword is already in alternating case
        if alternating in retVal:
            continue  # Skip, already processed
        
        # Use word boundaries to match whole words only
        pattern = r'\b' + keyword + r'\b'
        
        # Replace with alternating case
        retVal = re.sub(pattern, alternating, retVal, flags=re.IGNORECASE)
    
    return retVal
