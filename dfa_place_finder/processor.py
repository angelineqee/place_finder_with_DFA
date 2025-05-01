# dfa_place_finder/processor.py
"""
High-level operations:

• build_dfa()              → ready-made DFA instance + max phrase length
• scan_paragraph(text, dfa, max_len)
      returns (verdicts, bold_markdown)
"""

from __future__ import annotations

import re
from typing import List, Tuple

from .dfa import DFA
from .phrases import ACCEPTED_PHRASES
from .utils import strip_outer_punct, longest_phrase_len


# ------------------------------------------------------------------ #
#  (1) build_dfa  – called once, can be cached by Streamlit
# ------------------------------------------------------------------ #
def build_dfa() -> tuple[DFA, int]:
    dfa = DFA()
    for phrase in ACCEPTED_PHRASES:
        dfa.insert(phrase)
    return dfa, longest_phrase_len(ACCEPTED_PHRASES)

