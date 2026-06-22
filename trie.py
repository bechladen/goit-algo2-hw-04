from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class TrieNode:
    children: Dict[str, "TrieNode"] = field(default_factory=dict)
    value: Any = None
    is_end: bool = False
    subtree_words: int = 0  # кількість завершених слів у піддереві (включно з поточним вузлом)


class Trie:
    """
    Базове префіксне дерево.

    Підтримує додавання ключів через `put(key, value)`.
    """

    def __init__(self) -> None:
        self.root = TrieNode()
        self.size = 0

    def _find_node(self, s: str) -> Optional[TrieNode]:
        node = self.root
        for ch in s:
            nxt = node.children.get(ch)
            if nxt is None:
                return None
            node = nxt
        return node

    def _put(self, key: str, value: Any) -> bool:
        if not isinstance(key, str):
            raise TypeError("Ключ має бути рядком (str)")

        node = self.root
        path = [node]
        for ch in key:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            path.append(node)

        is_new_word = not node.is_end
        node.is_end = True
        node.value = value

        if is_new_word:
            self.size += 1
            for n in path:
                n.subtree_words += 1

        return is_new_word

    def put(self, key: str, value: Any) -> None:
        self._put(key, value)

    def __len__(self) -> int:
        return self.size

