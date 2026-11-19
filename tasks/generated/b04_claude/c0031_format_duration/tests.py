import random
from fractions import Fraction

import pytest
from solution import format_duration


@pytest.mark.parametrize(
    "seconds, max_units, expected",
    [
        (3725, 2, "1h 2m"),
        (86399, 2, "1d"),
        (0, 2, "0s"),
        (45, 2, "45s"),
        (3690, 2, "1h 2m"),
        (3689, 2, "1h 1m"),
        (90061, 4, "1d 1h 1m 1s"),
        (90000, 3, "1d 1h"),
        (86460, 2, "1d"),
        (3599, 1, "1h"),
        (3599, 2, "59m 59s"),
        (89, 1, "1m"),
        (90, 1, "2m"),
        (29, 1, "29s"),
        (59, 1, "59s"),
        (5400, 1, "2h"),
        (5399, 1, "1h"),
        (172799, 1, "2d"),
        (60, 3, "1m"),
        (10**9, 2, "11574d 2h"),
        (3600 * 24 * 3 + 1, 4, "3d 1s"),
    ],
)
def test_examples(seconds, max_units, expected):
    assert format_duration(seconds, max_units) == expected


def test_default_max_units():
    assert format_duration(3725) == "1h 2m"


@pytest.mark.parametrize("seconds, max_units", [(-1, 2), (10, 0), (10, -3)])
def test_invalid(seconds, max_units):
    with pytest.raises(ValueError):
        format_duration(seconds, max_units)


SIZES = [86400, 3600, 60, 1]
NAMES = "dhms"


def _oracle(seconds, k):
    if seconds == 0:
        return "0s"
    v = Fraction(seconds)
    for _ in range(3):
        top = next(i for i, s in enumerate(SIZES) if s <= v)
        units = list(range(top, min(top + k, 4)))
        step = SIZES[units[-1]]
        r = int(v / step + Fraction(1, 2)) * step
        new_top = next(i for i, s in enumerate(SIZES) if s <= r)
        if new_top == top:
            break
        v = Fraction(r)
    out = []
    for i in units:
        c, r = divmod(r, SIZES[i])
        if c:
            out.append(f"{c}{NAMES[i]}")
    return " ".join(out)


def test_random_against_oracle():
    rng = random.Random(7)
    for _ in range(300):
        s = rng.choice([rng.randint(0, 200), rng.randint(0, 10**6), rng.choice([59, 3599, 86399, 3570, 86370])])
        k = rng.randint(1, 4)
        assert format_duration(s, k) == _oracle(s, k), (s, k)
