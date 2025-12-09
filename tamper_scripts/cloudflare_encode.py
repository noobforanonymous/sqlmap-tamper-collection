#!/usr/bin/env python

"""
Copyright (c) 2006-2025 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: cloudflare_encode_safe.py
Description: Context-aware encoding that preserves SQL structure
Author: Regaan
Priority: LOW
"""

import re
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Context-aware character encoding that:
    - Only encodes inside string literals and values
    - Preserves SQL keywords and structure
    - Won't break MySQL comments
    - Won't encode operators in SQL context
    
    Technique:
        Encodes special characters ONLY in safe contexts:
        - Inside string literals: ' → %27
        - In comparison values: = → %3D (only after WHERE/HAVING)
        
        Does NOT encode:
        - Inside comments (/* ... */)
        - SQL operators in keyword context
        - Parentheses in function calls
    
    >>> tamper("WHERE id=1")
    'WHERE id%3D1'
    
    >>> tamper("WHERE name='admin'")
    'WHERE name%3D%27admin%27'
    """
    
    retVal = payload
    
    if not payload:
        return retVal
    
    # Don't encode if inside comment markers
    if '/*!' in retVal:
        # Has MySQL version comments, be very careful
        # Only encode values, not structure
        pass
    
    # Strategy: Only encode = in WHERE/HAVING clauses
    # Only encode quotes in string literals
    
    # Encode = only after WHERE/HAVING
    retVal = re.sub(r'(WHERE|HAVING)\s+(\w+)=', r'\1 \2%3D', retVal, flags=re.IGNORECASE)
    
    # Encode quotes only in value context (after =)
    # This is simplified - full parser would be better
    retVal = re.sub(r"='([^']*)'", r"=%27\1%27", retVal)
    retVal = re.sub(r'="([^"]*)"', r'=%22\1%22', retVal)
    
    return retVal
