import re
from collections import Counter

# Letters, optionally joined by ONE connector that has a letter on each side.
_WORD = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")


def _lower_ascii(s: str) -> str:
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)


def word_frequency(text: str, stop_words: list[str], min_letters: int, k: int) -> list[tuple[str, int]]:
    if k <= 0:
        return []
    stops = {_lower_ascii(w) for w in stop_words}
    counts: Counter = Counter()
    for m in _WORD.finditer(text):
        word = _lower_ascii(m.group())
        if word in stops:
            continue
        if sum(c.isalpha() for c in word) < min_letters:  # connectors are not letters
            continue
        counts[word] += 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
