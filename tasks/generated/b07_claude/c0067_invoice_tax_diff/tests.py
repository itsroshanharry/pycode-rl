import random
from decimal import ROUND_HALF_UP, Decimal

import pytest
from solution import invoice_tax_diff


@pytest.mark.parametrize(
    "lines, rate, expected",
    [
        ([5, 5, 5], 1000, (3, 2, 1)),
        ([], 2000, (0, 0, 0)),
        ([100], 0, (0, 0, 0)),
        ([-5], 1000, (-1, -1, 0)),
        ([-15], 1000, (-2, -2, 0)),
        ([-5, 5], 1000, (0, 0, 0)),
        ([-5, -5, -5], 1000, (-3, -2, -1)),
        ([4, 4, 4], 1000, (0, 1, -1)),
        ([1999, 2999, 1], 2000, (400 + 600 + 0, 1000, 0)),
        ([333, 333, 334], 1900, (63 + 63 + 63, 190, -1)),
        ([10 ** 15 + 5], 1000, (10 ** 14 + 1, 10 ** 14 + 1, 0)),
        ([1, 1, 1, 1], 5000, (4, 2, 2)),
        ([-1, -1, -1, -1], 5000, (-4, -2, -2)),
        ([12345], 825, (1018, 1018, 0)),
        ([25, -25, 25], 2000, (5, 5, 0)),
    ],
)
def test_examples(lines, rate, expected):
    assert tuple(invoice_tax_diff(lines, rate)) == expected


def test_invalid():
    with pytest.raises(ValueError):
        invoice_tax_diff([100], -1)


def _r(x):
    return int(x.quantize(Decimal(1), rounding=ROUND_HALF_UP))  # ROUND_HALF_UP in decimal = away from zero


def test_random_against_oracle():
    rng = random.Random(48)
    for _ in range(500):
        lines = [rng.randint(-5000, 5000) for _ in range(rng.randint(0, 8))]
        rate = rng.choice([0, 500, 825, 1000, 1900, 2000, 2500, 5000, 10000])
        pl = sum(_r(Decimal(n) * rate / 10000) for n in lines)
        pi = _r(Decimal(sum(lines)) * rate / 10000)
        assert tuple(invoice_tax_diff(lines, rate)) == (pl, pi, pl - pi), (lines, rate)
