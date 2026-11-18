import random
from fractions import Fraction

import pytest
from solution import mixed_number


@pytest.mark.parametrize(
    "n, d, expected",
    [
        (-10, 6, "-1 2/3"),
        (4, -6, "-2/3"),
        (0, 5, "0"),
        (0, -5, "0"),
        (6, 3, "2"),
        (-6, 3, "-2"),
        (-6, -3, "2"),
        (-4, -6, "2/3"),
        (7, 2, "3 1/2"),
        (1, 3, "1/3"),
        (-1, 3, "-1/3"),
        (100, 7, "14 2/7"),
        (-100, -7, "14 2/7"),
        (1, 1, "1"),
        (10**20 + 1, 10**20, "1 1/100000000000000000000"),
        (22, -8, "-2 3/4"),
    ],
)
def test_examples(n, d, expected):
    assert mixed_number(n, d) == expected


@pytest.mark.parametrize("n", [0, 5, -5])
def test_zero_denominator(n):
    with pytest.raises(ZeroDivisionError):
        mixed_number(n, 0)


def _oracle(n, d):
    f = Fraction(n, d)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    a = abs(f)
    whole = a.numerator // a.denominator
    frac = a - whole
    return f"{sign}{whole} {frac.numerator}/{frac.denominator}" if whole else f"{sign}{frac.numerator}/{frac.denominator}"


def test_random_against_oracle():
    rng = random.Random(78)
    for _ in range(300):
        n = rng.randint(-200, 200)
        d = rng.choice([i for i in range(-30, 31) if i])
        assert mixed_number(n, d) == _oracle(n, d), (n, d)
