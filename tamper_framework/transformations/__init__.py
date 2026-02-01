"""
Transformation Modules

Context-aware transformation rules for SQL tampering.

Author: Regaan
License: GPL v2
"""

# Core transformations
from tamper_framework.transformations.keyword_wrap import create_keyword_wrap_rule
from tamper_framework.transformations.space_replace import create_space_replace_rule
from tamper_framework.transformations.case_alternate import create_case_alternate_rule
from tamper_framework.transformations.value_encode import create_value_encode_rule

# Advanced transformations (v2.1.0+)
from tamper_framework.transformations.homoglyph import create_homoglyph_rule
from tamper_framework.transformations.function_wrap import create_function_wrap_rule
from tamper_framework.transformations.numeric_obfuscation import create_numeric_obfuscation_rule
from tamper_framework.transformations.comment_chaos import create_comment_chaos_rule
from tamper_framework.transformations.logical_operator_swap import create_logical_swap_rule
from tamper_framework.transformations.hex_encode import create_hex_encode_rule
from tamper_framework.transformations.version_comment_vary import create_version_comment_vary_rule

__all__ = [
    # Core
    'create_keyword_wrap_rule',
    'create_space_replace_rule',
    'create_case_alternate_rule',
    'create_value_encode_rule',
    
    # Advanced
    'create_homoglyph_rule',
    'create_function_wrap_rule',
    'create_numeric_obfuscation_rule',
    'create_comment_chaos_rule',
    'create_logical_swap_rule',
    'create_hex_encode_rule',
    'create_version_comment_vary_rule',
]
