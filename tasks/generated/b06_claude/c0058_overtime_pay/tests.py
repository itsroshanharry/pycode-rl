import random

import pytest
from solution import overtime_pay


@pytest.mark.parametrize(
    "days, rate, expected",
    [
        ([600, 600, 600, 600, 600, 0, 0], 6000, 354000),
        ([60] * 7, 6000, 45000),
        ([480] * 5 + [0, 0], 6000, 240000),
        ([0] * 7, 6000, 0),
        ([800, 0, 0, 0, 0, 0, 0], 6000, 100000),
        ([10] * 6 + [600], 6000, 102000),
        ([0] * 6 + [600], 6000, 66000),
        ([1, 0, 0, 0, 0, 0, 0], 30, 1),
        ([1, 0, 0, 0, 0, 0, 0], 29, 0),
        ([1, 0, 0, 0, 0, 0, 0], 31, 1),
        ([481, 0, 0, 0, 0, 0, 0], 40, 321),
        ([480] * 5 + [1, 0], 6000, 240150),
        ([480] * 4 + [481, 0, 0], 6000, 240150),
        ([1440, 1440, 0, 0, 0, 0, 0], 6000, 456000),
        ([1440] * 7, 100, 28800),
        ([600, 600, 600, 600, 600, 0, 0], 0, 0),
        ([700, 700, 700, 700, 0, 0, 0], 6000, 333000),
    ],
)
def test_examples(days, rate, expected):
    assert overtime_pay(days, rate) == expected


@pytest.mark.parametrize(
    "days, rate",
    [([0] * 6, 100), ([0] * 8, 100), ([1441, 0, 0, 0, 0, 0, 0], 100), ([-1, 0, 0, 0, 0, 0, 0], 100), ([0] * 7, -1)],
)
def test_invalid(days, rate):
    with pytest.raises(ValueError):
        overtime_pay(days, rate)


def _oracle(days, rate):
    # segment arithmetic instead of a minute loop: build (start, end, multiplier*2) pieces
    total, before = 0, 0
    seventh = min(days) > 0
    for i, m in enumerate(days):
        for k in range(m):
            daily = 2 if k < 480 else (3 if k < 720 else 4)
            weekly = 3 if before + k >= 2400 else 2
            sev = (3 if k < 480 else 4) if (seventh and i == 6) else 0
            total += max(daily, weekly, sev)
        before += m
    num = rate * total  # pay * 120
    q, r = divmod(num, 120)
    return q + (1 if 2 * r >= 120 else 0)


def test_random_against_oracle():
    rng = random.Random(47)
    for _ in range(150):
        days = [rng.choice([0, 0, 30, 479, 480, 481, 600, 720, 721, 900, 1440]) for _ in range(7)]
        if rng.random() < 0.3:
            days = [rng.randint(1, 800) for _ in range(7)]
        rate = rng.choice([0, 1, 29, 31, 1999, 4567])
        assert overtime_pay(days, rate) == _oracle(days, rate), (days, rate)
