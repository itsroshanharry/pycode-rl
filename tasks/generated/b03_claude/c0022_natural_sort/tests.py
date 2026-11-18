import functools
import random

import pytest
from solution import natural_sort


@pytest.mark.parametrize(
    "names, expected",
    [
        (["file10.txt", "file2.txt", "File1.txt"], ["File1.txt", "file2.txt", "file10.txt"]),
        (["a1", "a01", "a001"], ["a001", "a01", "a1"]),
        ([], []),
        (["b", "a", "B", "A"], ["A", "a", "B", "b"]),
        (["x9", "x10", "x9a", "x9.5"], ["x9", "x9.5", "x9a", "x10"]),
        (["1a", "a1", "10", "2"], ["1a", "2", "10", "a1"]),
        (["img12", "img", "img2"], ["img", "img2", "img12"]),
        (["v1.10", "v1.9", "v1.2.3"], ["v1.2.3", "v1.9", "v1.10"]),
        (["Straße", "STRASSE", "strasse"], ["STRASSE", "Straße", "strasse"]),
        (["a٣", "a3", "a2"], ["a2", "a3", "a٣"]),
        (["00", "0", "000"], ["0", "00", "000"]),
        (["z99999999999999999999", "z100000000000000000000"], ["z99999999999999999999", "z100000000000000000000"]),
        (["same", "same", "Same"], ["Same", "same", "same"]),
        (["a b", "a  b", "ab"], ["a  b", "a b", "ab"]),
    ],
)
def test_order(names, expected):
    assert list(natural_sort(names)) == expected


def _split(s):
    out, cur = [], ""
    for ch in s:
        if cur and (ch in "0123456789") != (cur[-1] in "0123456789"):
            out.append(cur)
            cur = ""
        cur += ch
    return out + ([cur] if cur else [])


def _cmp(a, b):
    ra, rb = _split(a), _split(b)
    for x, y in zip(ra, rb):
        dx, dy = x[0] in "0123456789", y[0] in "0123456789"
        if dx and dy and int(x) != int(y):
            return -1 if int(x) < int(y) else 1
        if dx != dy:
            return -1 if dx else 1
        if not dx and x.casefold() != y.casefold():
            return -1 if x.casefold() < y.casefold() else 1
    if len(ra) != len(rb):
        return -1 if len(ra) < len(rb) else 1
    return (a > b) - (a < b)


def test_random_against_comparator():
    rng = random.Random(16)
    pieces = ["a", "B", "b", "x", "0", "1", "2", "9", "10", "007", ".", "-", " ", "É", "é"]
    for _ in range(200):
        names = ["".join(rng.choice(pieces) for _ in range(rng.randint(0, 4))) for _ in range(rng.randint(0, 8))]
        assert list(natural_sort(names)) == sorted(names, key=functools.cmp_to_key(_cmp)), names
