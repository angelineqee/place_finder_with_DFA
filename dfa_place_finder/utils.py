# dfa_place_finder/utils.py
import string

__all__ = ["strip_outer_punct", "longest_phrase_len"]

def strip_outer_punct(tok: str) -> str:
    """Trim punctuation at both ends."""
    return tok.strip(string.punctuation)

def longest_phrase_len(phrases: list[str]) -> int:
    """Longest phrase length in *words*."""
    return max(len(p.split()) for p in phrases)
