import random
from decimal import Decimal

import pytest
from solution import histogram


def _oracle(values, lo, hi, width):
    # independent: Decimal arithmetic and explicit bin edges
    a, b, w = Decimal(lo), Decimal(hi), Decimal(width)
    edges = [a]
    while edges[-1] + w < b:
        edges.append(edges[-1] + w)
    edges.append(b)  # last edge is hi
    counts = [0] * (len(edges) - 1)
    under = over = 0
    for v in map(Decimal, values):
        if v < a:
            under += 1
        elif v > b:
            over += 1
        else:
            for i in range(len(counts)):
                last = i == len(counts) - 1
                if edges[i] <= v and (v < edges[i + 1] or (last and v <= edges[i + 1])):
                    counts[i] += 1
                    break
    return counts, under, over


CASES = [
    (["0", "0.1", "0.2", "0.3", "0.35", "1"], "0", "0.35", "0.1"),
    ([], "0", "1", "0.25"),
    (["0.3", "0.6", "0.9"], "0", "0.9", "0.3"),
    (["0.29999", "0.3", "0.30001"], "0", "0.6", "0.1"),
    (["-1", "-0.5", "0", "0.5", "1"], "-0.5", "0.5", "0.5"),
    (["5"], "5", "6", "10"),
    (["6"], "5", "6", "10"),
    (["10"], "0", "10", "3"),
    (["9", "9.999999", "10"], "0", "10", "3"),
    (["0.7", "0.8", "0.9", "1.0"], "0.7", "1.0", "0.1"),
    (["1000", "999.99"], "0", "1000", "100"),
    (["-0"], "-0.1", "0.1", "0.05"),
    (["12345678901234567890.1"], "12345678901234567890", "12345678901234567891", "0.1"),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], ([1, 1, 1, 2], 0, 1)),
    (CASES[2], ([0, 1, 2], 0, 0)),
    (CASES[3], ([0, 0, 1, 2, 0, 0], 0, 0)),
    (CASES[7], ([0, 0, 0, 1], 0, 0)),
]


@pytest.mark.parametrize("args", CASES)
def test_against_oracle(args):
    got = histogram(*args)
    assert (list(got[0]), got[1], got[2]) == _oracle(*args)


@pytest.mark.parametrize("args, expected", FIXED)
def test_fixed(args, expected):
    got = histogram(*args)
    assert (list(got[0]), got[1], got[2]) == expected


@pytest.mark.parametrize(
    "values, lo, hi, width",
    [([], "1", "1", "1"), ([], "2", "1", "1"), ([], "0", "1", "0"), ([], "0", "1", "-1"), (["x"], "0", "1", "1"),
     (["1e1"], "0", "1", "1"), ([".5"], "0", "1", "1"), (["5."], "0", "1", "1"), (["+1"], "0", "1", "1"),
     (["1"], "0", "1,5", "1"), (["１"], "0", "2", "1"), ([" 1"], "0", "2", "1")],
)
def test_invalid(values, lo, hi, width):
    with pytest.raises(ValueError):
        histogram(values, lo, hi, width)


def test_random_against_oracle():
    rng = random.Random(77)
    for _ in range(400):
        lo = rng.choice(["0", "-1", "0.1", "2.5"])
        hi = str(Decimal(lo) + Decimal(rng.choice(["0.3", "0.35", "1", "2.05", "0.9"])))
        width = rng.choice(["0.1", "0.05", "0.25", "0.3", "1"])
        vals = [str(Decimal(lo) + Decimal(rng.randint(-20, 300)) / 100) for _ in range(rng.randint(0, 12))]
        got = histogram(vals, lo, hi, width)
        assert (list(got[0]), got[1], got[2]) == _oracle(vals, lo, hi, width), (vals, lo, hi, width)
