import random
from fractions import Fraction

import pytest
from solution import allocate_cents


@pytest.mark.parametrize(
    "total, weights, expected",
    [
        (100, [1, 1, 1], [34, 33, 33]),
        (-100, [1, 1, 1], [-34, -33, -33]),
        (2, [1, 3], [0, 2]),
        (-2, [1, 3], [0, -2]),
        (0, [1, 2, 3], [0, 0, 0]),
        (10, [3, 2, 2, 3], [3, 2, 2, 3]),
        (5, [1, 2, 1], [1, 3, 1]),
        (1, [1, 1, 1, 1], [1, 0, 0, 0]),
        (3, [1, 1, 1, 1], [1, 1, 1, 0]),
        (1, [1, 2, 2, 1], [0, 1, 0, 0]),
        (2, [1, 2, 2, 1], [0, 1, 1, 0]),
        (7, [0, 5, 0], [0, 7, 0]),
        (1, [0, 1, 1], [0, 1, 0]),
        (101, [50, 50], [51, 50]),
        (-101, [50, 50], [-51, -50]),
        (1000, [333, 333, 334], [333, 333, 334]),
        (100, [2, 3, 5, 7], [12, 18, 29, 41]),
        (-100, [2, 3, 5, 7], [-12, -18, -29, -41]),
        (10 ** 20 + 1, [1, 1], [5 * 10 ** 19 + 1, 5 * 10 ** 19]),
        (4, [7], [4]),
        (-4, [7], [-4]),
    ],
)
def test_examples(total, weights, expected):
    assert list(allocate_cents(total, weights)) == expected


@pytest.mark.parametrize("weights", [[], [0], [0, 0], [-1, 2], [3, -1, 1]])
def test_invalid(weights):
    with pytest.raises(ValueError):
        allocate_cents(10, weights)


def _oracle(total, weights):
    sign, amount = (-1, -total) if total < 0 else (1, total)
    ideal = [Fraction(amount * w, sum(weights)) for w in weights]
    parts = [int(x) for x in ideal]  # floor (x >= 0)
    rank = sorted(range(len(weights)), key=lambda i: (ideal[i] - parts[i], weights[i], -i), reverse=True)
    for i in rank[: amount - sum(parts)]:
        parts[i] += 1
    return [sign * p for p in parts]


def test_random_against_oracle():
    rng = random.Random(72)
    for _ in range(500):
        weights = [rng.choice([0, 1, 1, 2, 3, 5, 10, 99]) for _ in range(rng.randint(1, 7))]
        if sum(weights) == 0:
            weights[0] = 1
        total = rng.randint(-1000, 1000)
        got = list(allocate_cents(total, weights))
        assert got == _oracle(total, weights), (total, weights)
        assert sum(got) == total
