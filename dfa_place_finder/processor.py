""" 
High-level operations:
 • build_dfa()              → ready-made DFA instance + max phrase length
 • scan_paragraph(text, dfa, max_len)       returns (verdicts, bold_markdown)
"""

from __future__ import annotations

import re
from typing import List, Tuple, Optional

from .dfa import DFA
from .phrases import ACCEPTED_PHRASES
from .utils import strip_outer_punct, longest_phrase_len


# ------------------------------------------------------------------ #
#  (1) build_dfa  – called once, can be cached by Streamlit
# ------------------------------------------------------------------ #
def build_dfa(custom_phrases: Optional[List[str]] = None) -> tuple[DFA, int]:
    """
    Build a DFA from a list of phrases.
    
    Parameters
    ----------
    custom_phrases : Optional list of custom phrases to use instead of defaults
                    If None, uses the default ACCEPTED_PHRASES
    
    Returns
    -------
    dfa : DFA instance
    max_len : longest phrase length (in words)
    """
    dfa = DFA()
    
    # Use custom phrases if provided, otherwise use default
    phrases_to_use = custom_phrases if custom_phrases is not None else ACCEPTED_PHRASES
    
    for phrase in phrases_to_use:
        dfa.insert(phrase)
        
    return dfa, longest_phrase_len(phrases_to_use)


# ------------------------------------------------------------------ #
#  (2) scan_paragraph
# ------------------------------------------------------------------ #
def scan_paragraph(
    paragraph: str, dfa: DFA, max_len: int
) -> tuple[List[Tuple[str, bool]], str]:
    """
    Parameters
    ----------
    paragraph : raw user text
    dfa       : built DFA
    max_len   : longest phrase length (in words)
    
    Returns
    -------
    verdicts        : list[(token|phrase, accepted?)]
    bold_paragraph  : the paragraph with accepted items **boldfaced**
                      (Markdown syntax, safe from nested bold)
    """
    # ---- tokenise ----
    tokens = [tok for w in paragraph.split() if (tok := strip_outer_punct(w))]
    
    verdicts: list[tuple[str, bool]] = []
    accepted_set: set[str] = set()
    
    i, n = 0, len(tokens)
    while i < n:
        match = None
        for L in range(min(max_len, n - i), 0, -1):
            cand = " ".join(tokens[i : i + L])
            if dfa.accepts(cand):
                match = cand
                break
        
        if match:
            verdicts.append((match, True))
            accepted_set.add(match)
            i += len(match.split())
        else:
            tok = tokens[i]
            ok = dfa.accepts(tok)
            verdicts.append((tok, ok))
            if ok:
                accepted_set.add(tok)
            i += 1
    
    # ---- build bold paragraph (placeholder trick avoids nested bold) ----
    placeholders: dict[str, str] = {}
    bold_para = paragraph
    for idx, phrase in enumerate(sorted(accepted_set, key=len, reverse=True)):
        ph = f"\u0001{idx}\u0002"                 # control chars unlikely in text
        placeholders[ph] = f'<span style="background-color: #d1ffd1; color: green; font-weight: bold; border-radius: 4px; padding: 2px 4px">{phrase}</span>'
        pattern = re.compile(rf"(?<!\w)({re.escape(phrase)})(?!\w)")
        bold_para = pattern.sub(ph, bold_para)
    
    for ph, boldver in placeholders.items():
        bold_para = bold_para.replace(ph, boldver)
    
    return verdicts, bold_para