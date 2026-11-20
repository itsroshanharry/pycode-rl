import random
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction

import pytest
from solution import percentile

V = [15, 20, 35, 40, 50]


@pytest.mark.parametrize(
    "values, p, method, expected",
    [
        (V, "40", "linear", "29.000000"),
        ([1, 2, 3, 4], "50", "nearest", "3.000000"),
        ([1, 2, 3, 4, 5, 6], "50", "nearest", "3.000000"),
        ([1, 2, 3, 4], "50", "linear", "2.500000"),
        ([1, 2, 3, 4], "50", "lower", "2.000000"),
        ([1, 2, 3, 4], "50", "higher", "3.000000"),
        ([1, 2, 3, 4], "50", "midpoint", "2.500000"),
        ([4, 1, 3, 2], "50", "linear", "2.500000"),
        (V, "0", "linear", "15.000000"),
        (V, "100", "linear", "50.000000"),
        (V, "100.0", "higher", "50.000000"),
        (V, "25", "lower", "20.000000"),
        (V, "25", "higher", "20.000000"),
        (V, "30", "linear", "23.000000"),
        (V, "30", "lower", "20.000000"),
        (V, "30", "higher", "35.000000"),
        (V, "30", "midpoint", "27.500000"),
        (V, "30", "nearest", "20.000000"),
        (V, "40", "nearest", "35.000000"),
        (V, "37.5", "nearest", "35.000000"),
        (V, "62.5", "nearest", "35.000000"),
        (V, "87.5", "nearest", "50.000000"),
        ([7], "73", "linear", "7.000000"),
        ([1, 2], "33.3333333", "linear", "1.333333"),
        ([0, 1], "0.00005", "linear", "0.000000"),
        ([0, 1], "0.00015", "linear", "0.000002"),
        ([0, 1], "0.00025", "linear", "0.000002"),
        ([-3, -1], "50", "linear", "-2.000000"),
        ([-1, 0], "99.99995", "linear", "0.000000"),
        ([-1, 0], "99.9999", "linear", "-0.000001"),
        ([1, 3], "50", "midpoint", "2.000000"),
        ([-5, 2], "10", "midpoint", "-1.500000"),
        ([10 ** 18, 10 ** 18 + 1], "50", "linear", "1000000000000000000.500000"),
    ],
)
def test_examples(values, p, method, expected):
    assert percentile(values, p, method) == expected


@pytest.mark.parametrize(
    "values, p, method",
    [([], "50", "linear"), ([1], "50", "median"), ([1], "101", "linear"), ([1], "100.5", "linear"), ([1], "-1", "linear"),
     ([1], "", "linear"), ([1], ".5", "linear"), ([1], "50.", "linear"), ([1], "1e1", "linear"), ([1], " 50", "linear"),
     ([1], "５０", "linear"), ([1], "1000", "linear")],
)
def test_invalid(values, p, method):
    with pytest.raises(ValueError):
        percentile(values, p, method)


def _oracle(values, p, method):
    xs = sorted(values)
    h = (len(xs) - 1) * Fraction(p) / 100
    lo = int(h)
    hi = min(lo + 1, len(xs) - 1) if h != lo else lo
    if method == "linear":
        r = xs[lo] + (h - lo) * (xs[hi] - xs[lo])
    elif method == "lower":
        r = Fraction(xs[lo])
    elif method == "higher":
        r = Fraction(xs[hi])
    elif method == "midpoint":
        r = Fraction(xs[lo] + xs[hi], 2)
    else:
        r = Fraction(xs[round(h)])  # Python's round(Fraction) is half-to-even
    with localcontext() as ctx:
        ctx.prec = 80
        d = (Decimal(r.numerator) / Decimal(r.denominator)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)
    s = f"{d:.6f}"
    return "0.000000" if s == "-0.000000" else s


def test_random_against_oracle():
    rng = random.Random(76)
    for _ in range(600):
        values = [rng.randint(-50, 50) for _ in range(rng.randint(1, 9))]
        p = rng.choice(["0", "1", "10", "12.5", "25", "33.3", "50", "62.5", "75", "87.5", "99.9", "100"])
        m = rng.choice(["linear", "lower", "higher", "nearest", "midpoint"])
        assert percentile(values, p, m) == _oracle(values, p, m), (values, p, m)
