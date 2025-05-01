# dfa_place_finder/processor.py
"""
High-level operations:

• build_dfa()              → ready-made DFA instance + max phrase length
• scan_paragraph(text, dfa, max_len)
      returns (verdicts, bold_markdown)
"""
