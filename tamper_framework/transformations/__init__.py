"""
Transformation Modules

Context-aware transformation rules for SQL tampering.

Author: Regaan
License: GPL v2
"""

from tamper_framework.transformations.keyword_wrap import create_keyword_wrap_rule
from tamper_framework.transformations.space_replace import create_space_replace_rule
from tamper_framework.transformations.case_alternate import create_case_alternate_rule
from tamper_framework.transformations.value_encode import create_value_encode_rule

__all__ = [
    'create_keyword_wrap_rule',
    'create_space_replace_rule',
    'create_case_alternate_rule',
    'create_value_encode_rule',
]
