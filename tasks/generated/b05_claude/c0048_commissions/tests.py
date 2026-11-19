import random
from fractions import Fraction

import pytest
from solution import commissions


@pytest.mark.parametrize(
    "sales, tiers, expected",
    [
        ([100000, 50000], [(0, 500), (120000, 1000)], [5000, 4000]),
        ([1, 1, 1], [(0, 5000)], [1, 0, 1]),
        ([], [(0, 100)], []),
        ([200, -200], [(0, 1000)], [20, -20]),
        ([-100, 300], [(0, 1000)], [0, 20]),
        ([-100, 50], [(0, 1000)], [0, 0]),
        ([120000], [(0, 500), (120000, 1000)], [6000]),
        ([120001], [(0, 500), (120000, 1000)], [6000]),
        ([120005], [(0, 500), (120000, 1000)], [6001]),
        ([130000, -20000], [(0, 500), (120000, 1000)], [7000, -1500]),
        ([50, 50, 50], [(0, 0), (100, 10000)], [0, 0, 50]),
        ([99, 2], [(0, 0), (100, 10000)], [0, 1]),
        ([10, 10, 10, 10], [(0, 2500)], [3, 2, 3, 2]),
        ([10 ** 12], [(0, 1), (10 ** 6, 2), (10 ** 9, 3)], [299899900]),
        ([3, 3, 3], [(0, 1666)], [0, 1, 0]),
        ([1, 1], [(0, 4999)], [0, 1]),
        ([1, 1], [(0, 5001)], [1, 0]),
        ([150000, 1], [(0, 500), (120000, 1000), (150000, 0)], [9000, 0]),
    ],
)
def test_examples(sales, tiers, expected):
    assert list(commissions(sales, tiers)) == expected


@pytest.mark.parametrize(
    "tiers",
    [[], [(1, 100)], [(0, 100), (0, 200)], [(0, 100), (50, 200), (40, 300)], [(0, -1)], [(0, 100), (10, -5)]],
)
def test_invalid(tiers):
    with pytest.raises(ValueError):
        commissions([100], tiers)


def _oracle(sales, tiers):
    def owed(x):
        if x <= 0:
            return Fraction(0)
        total = Fraction(0)
        bounds = [t for t, _ in tiers] + [None]
        for (lo, rate), hi in zip(tiers, bounds[1:]):
            part = max(0, (x if hi is None else min(x, hi)) - lo)
            total += Fraction(part * rate, 10000)
        return total

    def rnd(f):
        return int(f + Fraction(1, 2)) if f >= 0 else None  # floor(f + 1/2) for f >= 0

    out, run, prev = [], 0, 0
    for s in sales:
        run += s
        r = rnd(owed(run))
        out.append(r - prev)
        prev = r
    return out


def test_random_against_oracle():
    rng = random.Random(50)
    for _ in range(300):
        thresholds = sorted(rng.sample(range(1, 5000), rng.randint(0, 4)))
        tiers = [(0, rng.choice([0, 1, 250, 333, 5000]))] + [(t, rng.choice([0, 1, 100, 777, 2500, 10000])) for t in thresholds]
        sales = [rng.randint(-3000, 6000) for _ in range(rng.randint(0, 8))]
        got = list(commissions(sales, tiers))
        assert got == _oracle(sales, tiers), (sales, tiers)
