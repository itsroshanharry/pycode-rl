import random

import pytest
from solution import word_frequency


def _oracle(text, stops, min_letters, k):
    # independent: explicit character-by-character state machine
    words, cur, i = [], "", 0
    letters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    while i < len(text):
        ch = text[i]
        if ch in letters:
            cur += ch
        elif ch in "'-" and cur and cur[-1] in letters and i + 1 < len(text) and text[i + 1] in letters:
            cur += ch
        else:
            if cur:
                words.append(cur)
            cur = ""
        i += 1
    if cur:
        words.append(cur)
    low = lambda s: "".join(c.lower() if c in letters else c for c in s)
    stop = {low(s) for s in stops}
    counts = {}
    for w in map(low, words):
        if w in stop or sum(c in letters for c in w) < min_letters:
            continue
        counts[w] = counts.get(w, 0) + 1
    if k <= 0:
        return []
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


CASES = [
    ("The cat's toy; the CAT's toy -- the end!", ["the"], 3, 2),
    ("", [], 1, 5),
    ("a b c", [], 1, 0),
    ("a b c", [], 1, -1),
    ("well--known well-known WELL-KNOWN", [], 1, 10),
    ("'quoted' dogs' 'x' -dash- end-", [], 1, 10),
    ("rock'n'roll rock'n'roll rock'-n roll", [], 1, 10),
    ("re-use re use Re-Use", ["RE"], 1, 10),
    ("a-b a b ab", [], 2, 10),
    ("abc123def 4you", [], 1, 10),
    ("café naïve Ａbc", [], 1, 10),
    ("zeta alpha beta alpha zeta beta gamma", [], 1, 3),
    ("I i I a A", ["A"], 1, 5),
    ("x" * 3 + " " + "y" * 3, ["XXX"], 1, 5),
    ("don't Don't DON'T dont", [], 1, 5),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], [("cat's", 2), ("toy", 2)]),
    (CASES[4], [("well-known", 2), ("known", 1), ("well", 1)]),
    (CASES[5], [("dash", 1), ("dogs", 1), ("end", 1), ("quoted", 1), ("x", 1)]),
    (CASES[8], [("a-b", 1), ("ab", 1)]),
]


@pytest.mark.parametrize("args", CASES)
def test_against_oracle(args):
    assert [tuple(x) for x in word_frequency(*args)] == _oracle(*args)


@pytest.mark.parametrize("args, expected", FIXED)
def test_fixed(args, expected):
    assert [tuple(x) for x in word_frequency(*args)] == expected


def test_random_against_oracle():
    rng = random.Random(100)
    pieces = ["ab", "Ab", "AB", "c", "'", "-", "--", " ", " ", "1", "é", "don't", "x-y", ".", "''"]
    for _ in range(500):
        text = "".join(rng.choice(pieces) for _ in range(rng.randint(0, 25)))
        stops = rng.sample(["ab", "C", "x-y", "DON'T", "zz"], rng.randint(0, 3))
        args = (text, stops, rng.randint(0, 3), rng.randint(-1, 6))
        assert [tuple(x) for x in word_frequency(*args)] == _oracle(*args), args
