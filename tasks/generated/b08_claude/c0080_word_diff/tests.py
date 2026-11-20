import random
import sys
from functools import lru_cache

import pytest
from solution import word_diff


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("the quick brown fox", "the slow brown dog",
         [("=", "the"), ("-", "quick"), ("+", "slow"), ("=", "brown"), ("-", "fox"), ("+", "dog")]),
        ("", "", []),
        ("a b", "", [("-", "a"), ("-", "b")]),
        ("", "a b", [("+", "a"), ("+", "b")]),
        ("a b c", "a b c", [("=", "a"), ("=", "b"), ("=", "c")]),
        ("  a \t b\n", "a b", [("=", "a"), ("=", "b")]),
        ("a b", "b a", [("-", "a"), ("=", "b"), ("+", "a")]),
        ("x", "y", [("-", "x"), ("+", "y")]),
        ("A b", "a b", [("-", "A"), ("+", "a"), ("=", "b")]),
        ("a b c d", "a x c y", [("=", "a"), ("-", "b"), ("+", "x"), ("=", "c"), ("-", "d"), ("+", "y")]),
        ("a a b", "a b b", [("=", "a"), ("-", "a"), ("=", "b"), ("+", "b")]),
        ("b c a", "a b c", [("+", "a"), ("=", "b"), ("=", "c"), ("-", "a")]),
        ("1 2 3 4 5", "5 4 3 2 1", [("-", "1"), ("-", "2"), ("-", "3"), ("-", "4"), ("=", "5"), ("+", "4"), ("+", "3"), ("+", "2"), ("+", "1")]),
    ],
)
def test_examples(a, b, expected):
    assert [tuple(o) for o in word_diff(a, b)] == expected


def _oracle(a, b):
    x, y = tuple(a.split()), tuple(b.split())
    sys.setrecursionlimit(10000)

    @lru_cache(maxsize=None)
    def L(i, j):
        if i == len(x) or j == len(y):
            return 0
        if x[i] == y[j]:
            return 1 + L(i + 1, j + 1)
        return max(L(i + 1, j), L(i, j + 1))

    ops, i, j = [], 0, 0
    while i < len(x) or j < len(y):
        if i < len(x) and j < len(y) and x[i] == y[j]:
            ops.append(("=", x[i])); i += 1; j += 1
        elif j == len(y) or (i < len(x) and L(i + 1, j) >= L(i, j + 1)):
            ops.append(("-", x[i])); i += 1
        else:
            ops.append(("+", y[j])); j += 1
    return ops, L(0, 0)


def test_random_against_oracle():
    rng = random.Random(102)
    for _ in range(300):
        a = " ".join(rng.choice(["a", "b", "c", "A"]) for _ in range(rng.randint(0, 12)))
        b = rng.choice([" ", "  ", "\t"]).join(rng.choice(["a", "b", "c", "d"]) for _ in range(rng.randint(0, 12)))
        got = [tuple(o) for o in word_diff(a, b)]
        want, lcs = _oracle(a, b)
        assert got == want, (a, b)
        assert [w for op, w in got if op != "+"] == a.split()
        assert [w for op, w in got if op != "-"] == b.split()
        assert sum(op == "=" for op, _ in got) == lcs


def test_largest_allowed():
    rng = random.Random(300)
    a = " ".join(rng.choice("abcdefghij") for _ in range(300))
    b = " ".join(rng.choice("abcdefghij") for _ in range(300))
    got = [tuple(o) for o in word_diff(a, b)]
    assert [w for op, w in got if op != "+"] == a.split()
    assert [w for op, w in got if op != "-"] == b.split()
    assert got == _oracle(a, b)[0]
