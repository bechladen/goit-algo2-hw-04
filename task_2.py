from __future__ import annotations

from typing import Any, Optional

from trie import Trie, TrieNode


class Homework(Trie):
    """
    Розширення Trie для домашнього завдання:
    - підрахунок слів за суфіксом (через окреме "реверсне" Trie),
    - перевірка наявності хоча б одного слова з заданим префіксом.
    """

    def __init__(self) -> None:
        super().__init__()
        self._suffix_root = TrieNode()

    def _suffix_find_node(self, s_reversed: str) -> Optional[TrieNode]:
        node = self._suffix_root
        for ch in s_reversed:
            nxt = node.children.get(ch)
            if nxt is None:
                return None
            node = nxt
        return node

    def _suffix_put(self, key_reversed: str) -> None:
        node = self._suffix_root
        node.subtree_words += 1
        for ch in key_reversed:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
            node.subtree_words += 1
        node.is_end = True

    def put(self, key: str, value: Any) -> None:
        """
        Додаємо слово в основне Trie та (якщо це нове слово) у "реверсне" Trie для суфіксів.
        """

        is_new_word = self._put(key, value)
        if is_new_word:
            self._suffix_put(key[::-1])

    def count_words_with_suffix(self, pattern) -> int:
        if not isinstance(pattern, str):
            raise TypeError("pattern має бути рядком (str)")

        node = self._suffix_find_node(pattern[::-1])
        return 0 if node is None else int(node.subtree_words)

    def has_prefix(self, prefix) -> bool:
        if not isinstance(prefix, str):
            raise TypeError("prefix має бути рядком (str)")

        node = self._find_node(prefix)
        return False if node is None else node.subtree_words > 0


if __name__ == "__main__":
    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    # Перевірка кількості слів, що закінчуються на заданий суфікс
    assert trie.count_words_with_suffix("e") == 1  # apple
    assert trie.count_words_with_suffix("ion") == 1  # application
    assert trie.count_words_with_suffix("a") == 1  # banana
    assert trie.count_words_with_suffix("at") == 1  # cat

    # Перевірка наявності префікса
    assert trie.has_prefix("app") is True  # apple, application
    assert trie.has_prefix("bat") is False
    assert trie.has_prefix("ban") is True  # banana
    assert trie.has_prefix("ca") is True  # cat

    print("OK")

