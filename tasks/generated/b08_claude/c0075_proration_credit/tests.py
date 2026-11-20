import random
from datetime import date, timedelta
from fractions import Fraction

import pytest
from solution import proration_credit


@pytest.mark.parametrize(
    "start, end, change, old, new, expected",
    [
        ("2024-01-01", "2024-02-01", "2024-01-16", 1000, 2000, 516),
        ("2024-01-01", "2024-02-01", "2024-01-16", 2000, 1000, -516),
        ("2024-01-01", "2024-02-01", "2024-01-01", 1000, 2000, 1000),
        ("2024-01-01", "2024-02-01", "2024-01-31", 1000, 2000, 32),
        ("2024-01-01", "2024-02-01", "2024-01-16", 1500, 1500, 0),
        ("2024-01-01", "2024-01-03", "2024-01-02", 0, 1, 1),
        ("2024-01-01", "2024-01-03", "2024-01-02", 1, 0, -1),
        ("2024-01-01", "2024-01-03", "2024-01-02", 0, 3, 2),
        ("2024-01-01", "2024-01-03", "2024-01-02", 3, 0, -2),
        ("2024-02-01", "2024-03-01", "2024-02-15", 0, 2900, 1500),
        ("2023-02-01", "2023-03-01", "2023-02-15", 0, 2800, 1400),
        ("2023-12-15", "2024-01-15", "2024-01-01", 0, 3100, 1400),
        ("2024-01-01", "2025-01-01", "2024-07-02", 0, 36600, 18300),
        ("2024-01-01", "2024-01-02", "2024-01-01", 999, 0, -999),
    ],
)
def test_examples(start, end, change, old, new, expected):
    assert proration_credit(start, end, change, old, new) == expected


@pytest.mark.parametrize(
    "start, end, change, old, new",
    [
        ("2024-01-01", "2024-01-01", "2024-01-01", 0, 1),
        ("2024-02-01", "2024-01-01", "2024-01-15", 0, 1),
        ("2024-01-01", "2024-02-01", "2024-02-01", 0, 1),
        ("2024-01-01", "2024-02-01", "2023-12-31", 0, 1),
        ("2024-01-01", "2024-02-01", "2024-01-15", -1, 1),
        ("2024-01-01", "2024-02-01", "2024-01-15", 1, -1),
        ("2024-1-01", "2024-02-01", "2024-01-15", 0, 1),
        ("2024-01-01", "2024-02-30", "2024-01-15", 0, 1),
        ("2024/01/01", "2024-02-01", "2024-01-15", 0, 1),
        ("2024-01-01", "2024-02-01", "2024-01-15T00:00", 0, 1),
    ],
)
def test_invalid(start, end, change, old, new):
    with pytest.raises(ValueError):
        proration_credit(start, end, change, old, new)


def test_random_against_oracle():
    rng = random.Random(49)
    for _ in range(500):
        s = date(2023, 1, 1) + timedelta(days=rng.randrange(800))
        e = s + timedelta(days=rng.randint(1, 400))
        c = s + timedelta(days=rng.randrange((e - s).days))
        old, new = rng.randint(0, 5000), rng.randint(0, 5000)
        x = Fraction((new - old) * (e - c).days, (e - s).days)
        mag = int(abs(x) + Fraction(1, 2))
        want = mag if x >= 0 else -mag
        assert proration_credit(s.isoformat(), e.isoformat(), c.isoformat(), old, new) == want
