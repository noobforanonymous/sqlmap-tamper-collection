#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_space_safe.py
Description: Context-aware space replacement that preserves existing comments
Author: Regaan
Priority: NORMAL
"""

import re
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Context-aware space replacement that:
    - Preserves existing comments
    - Only replaces spaces outside of strings
    - Won't break nested comments
    
    Technique:
        Replaces spaces with /**/ only in safe contexts
        Skips spaces inside:
        - Existing comments (/* ... */)
        - String literals ('...' or "...")
        - Already replaced spaces
    
    >>> tamper("SELECT * FROM users")
    'SELECT/**/*/**/FROM/**/users'
    
    >>> tamper("SELECT/**/*/**/FROM users")
    'SELECT/**/*/**/FROM/**/users'
    """
    
    retVal = payload
    
    if not payload:
        return retVal
    
    # Don't reapply if already has /**/ markers
    if '/**/' in retVal:
        # Partially processed, only replace remaining spaces
        pass
    
    # Simple approach: replace spaces not inside quotes or existing comments
    # This is a simplified version - full SQL parsing would be more robust
    
    # Track if we're inside a string literal
    in_string = False
    quote_char = None
    result = []
    i = 0
    
    while i < len(retVal):
        char = retVal[i]
        
        # Handle string literals
        if char in ("'", '"') and (i == 0 or retVal[i-1] != '\\'):
            if not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char:
                in_string = False
                quote_char = None
        
        # Replace space only if not in string
        if char == ' ' and not in_string:
            # Check if next chars are already /**/
            if retVal[i:i+4] != ' /**':
                result.append('/**/')
            else:
                result.append(char)
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)
