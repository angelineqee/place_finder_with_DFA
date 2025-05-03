# dfa_place_finder/dfa.py
from __future__ import annotations
import string


class DFA:
    """Deterministic Finite Automaton implemented as a character-trie."""

    class _Node:
        __slots__ = ("children", "is_final")

        def __init__(self):
            self.children: dict[str, DFA._Node] = {}
            self.is_final = False

    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        self._root = self._Node()
        self._trap_node = self._Node()

    def insert(self, word: str) -> None:
        node = self._root
        for ch in word:
            node = node.children.setdefault(ch, self._Node())
        node.is_final = True

    def accepts(self, text: str) -> bool:
        node = self._root
        for ch in text:
            if ch in string.punctuation:          # ignore interior punct
                continue
            if ch not in node.children:
                node = self._trap_node
                break
            else:
                node = node.children[ch]
        if node == self._trap_node:
            return False
        return node.is_final
