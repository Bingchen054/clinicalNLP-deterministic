"""
criteria_extractor.py

This module is intentionally disabled.

We no longer extract criteria dynamically.
Canonical criteria are defined in mcg_criteria.py
and loaded directly by alignment_engine.
"""

from typing import Dict, List
from alignment_types import ExtractedCriterion  # type: ignore

def extract_criteria(sections: Dict[str, List[str]]) -> List[ExtractedCriterion]:
    """
    Disabled extractor.
    Always returns empty list.
    """
    return []