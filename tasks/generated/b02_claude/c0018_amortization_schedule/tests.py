import math
import random
from fractions import Fraction

import pytest
from solution import amortization_schedule


def _norm(result):
    return [tuple(x) for x in result]


@pytest.mark.parametrize(
    "p, bp, m, expected",
    [
        (100000, 1200, 3, [(34002, 1000, 33002), (34002, 670, 33332), (34003, 337, 33666)]),
        (100, 0, 3, [(33, 0, 33), (33, 0, 33), (34, 0, 34)]),
        (0, 500, 2, [(0, 0, 0), (0, 0, 0)]),
        (5000, 0, 1, [(5000, 0, 5000)]),
        (10000, 1200, 1, [(10100, 100, 10000)]),
        (200, 0, 3, [(67, 0, 67), (67, 0, 67), (66, 0, 66)]),
        (99, 0, 2, [(50, 0, 50), (49, 0, 49)]),
    ],
)
def test_examples(p, bp, m, expected):
    assert _norm(amortization_schedule(p, bp, m)) == expected


@pytest.mark.parametrize("p, bp, m", [(-1, 100, 3), (100, -1, 3), (100, 100, 0), (100, 100, -2)])
def test_invalid(p, bp, m):
    with pytest.raises(ValueError):
        amortization_schedule(p, bp, m)


def _half_up(x):
    return math.floor(x + Fraction(1, 2))


def _check_properties(p, bp, m, rows):
    r = Fraction(bp, 120000)
    assert len(rows) == m
    assert sum(row[2] for row in rows) == p  # the loan is fully repaid
    regular = _half_up(Fraction(p, m) if r == 0 else p * r / (1 - (1 + r) ** -m))
    balance = p
    for i, (pay, interest, part) in enumerate(rows):
        assert interest == _half_up(balance * r)
        assert pay == interest + part
        if i < m - 1:
            assert pay == regular
        else:
            assert part == balance
        balance -= part
    assert balance == 0


def test_random_properties():
    rng = random.Random(41)
    for _ in range(120):
        p, bp, m = rng.randint(0, 5_000_000), rng.choice([0, rng.randint(1, 3000)]), rng.randint(1, 60)
        _check_properties(p, bp, m, _norm(amortization_schedule(p, bp, m)))


def test_long_loan_is_exact():
    rows = _norm(amortization_schedule(30_000_000, 650, 360))
    _check_properties(30_000_000, 650, 360, rows)
    assert rows[0] == (189620, 162500, 27120)
