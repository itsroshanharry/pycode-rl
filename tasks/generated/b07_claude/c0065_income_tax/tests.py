import random
from fractions import Fraction

import pytest
from solution import income_tax

B = [(2000, 20), (None, 40)]


@pytest.mark.parametrize(
    "income, allowance, threshold, bands, expected",
    [
        (5002, 1000, 5000, B, 1201),
        (900, 1000, 5000, B, 0),
        (1000, 1000, 5000, B, 0),
        (3000, 1000, 5000, B, 400),
        (5000, 1000, 5000, B, 1200),
        (5001, 1000, 5000, B, 1200),
        (5003, 1000, 5000, B, 1201),
        (7000, 1000, 5000, B, 2400),
        (7001, 1000, 5000, B, 2400),
        (10000, 1000, 5000, B, 3600),
        (0, 0, 0, B, 0),
        (3003, 1000, 5000, [(2001, 15), (None, 45)], 301),
        (3001, 1000, 5000, [(2001, 15), (None, 45)], 300),
        (100, 0, 0, [(None, 33)], 33),
        (101, 0, 0, [(None, 33)], 33),
        (10 ** 12, 1257000, 10000000, [(3770000, 20), (8743000, 40), (None, 45)],
         (3770000 * 20 + 8743000 * 40 + (10 ** 12 - 3770000 - 8743000) * 45) // 100),
        (5000, 0, 0, [(1000, 0), (1000, 100), (None, 0)], 1000),
        (500, 1000, 5000, [(None, 100)], 0),
        (3001, 1000, 5000, [(2000, 20), (None, 100)], 401),
        # allowance fully tapered away (reduction 1285000 > 1257000): floors at 0
        (12570000 + 1, 1257000, 10000000, [(None, 40)], 12570001 * 40 // 100),
        (10000001, 1257000, 10000000, [(None, 40)], (10000001 - 1257000) * 40 // 100),
        (10000003, 1257000, 10000000, [(None, 40)], (10000003 - 1256999) * 40 // 100),
    ],
)
def test_examples(income, allowance, threshold, bands, expected):
    assert income_tax(income, allowance, threshold, bands) == expected


@pytest.mark.parametrize(
    "args",
    [
        (-1, 0, 0, B), (0, -1, 0, B), (0, 0, -1, B), (100, 0, 0, []), (100, 0, 0, [(None, 20), (None, 40)]),
        (100, 0, 0, [(1000, 20)]), (100, 0, 0, [(0, 20), (None, 40)]), (100, 0, 0, [(100, 101), (None, 40)]),
        (100, 0, 0, [(100, -1), (None, 40)]), (100, 0, 0, [(None, 20), (100, 40)]),
    ],
)
def test_invalid(args):
    with pytest.raises(ValueError):
        income_tax(*args)


def _oracle(income, allowance, threshold, bands):
    eff = allowance
    if income > threshold:
        eff = max(0, allowance - (income - threshold) // 2)
    taxable = max(0, income - eff)
    total, lo = Fraction(0), 0
    for width, rate in bands:
        hi = None if width is None else lo + width
        part = max(0, (taxable if hi is None else min(taxable, hi)) - lo)
        total += Fraction(part * rate, 100)
        if hi is None:
            break
        lo = hi
    return int(total)  # floor, total >= 0


def test_random_against_oracle():
    rng = random.Random(39)
    for _ in range(500):
        bands = [(rng.randint(1, 3000), rng.randint(0, 100)) for _ in range(rng.randint(0, 3))] + [(None, rng.randint(0, 100))]
        income, allowance, threshold = rng.randint(0, 20000), rng.randint(0, 5000), rng.randint(0, 15000)
        assert income_tax(income, allowance, threshold, bands) == _oracle(income, allowance, threshold, bands)
