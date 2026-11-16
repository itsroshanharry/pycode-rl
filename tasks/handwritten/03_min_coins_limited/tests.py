import random

import pytest
from solution import min_coins_limited


@pytest.mark.parametrize(
    "amount, coins, expected",
    [
        (11, [(5, 1), (2, 5), (1, 0)], 4),
        (3, [(2, 3)], -1),
        (0, [], 0),
        (0, [(5, 3)], 0),
        (7, [], -1),
        (6, [(1, 6)], 6),
        (6, [(1, 5)], -1),
        (6, [(4, 1), (3, 2)], 2),
        (10, [(5, 1), (5, 1)], 2),
        (10, [(5, 1)], -1),
        (30, [(25, 1), (10, 3), (1, 5)], 3),
        (63, [(1, 100), (2, 100), (4, 100), (8, 100), (16, 100), (32, 100)], 6),
        (4, [(4, 0), (2, 2)], 2),
        (9999, [(1, 10000)], 9999),
        (10000, [(10000, 1), (1, 9999)], 1),
    ],
)
def test_examples(amount, coins, expected):
    assert min_coins_limited(amount, coins) == expected


def _oracle(amount, coins):
    # Expand every coin individually and run a plain 0/1 knapsack.
    best = [0] + [None] * amount
    for value, count in coins:
        for _ in range(count):
            for a in range(amount, value - 1, -1):
                if best[a - value] is not None and (best[a] is None or best[a - value] + 1 < best[a]):
                    best[a] = best[a - value] + 1
    return -1 if best[amount] is None else best[amount]


def test_random_against_oracle():
    rng = random.Random(42)
    for _ in range(120):
        coins = [(rng.randint(1, 12), rng.randint(0, 4)) for _ in range(rng.randint(0, 5))]
        amount = rng.randint(0, 40)
        assert min_coins_limited(amount, coins) == _oracle(amount, coins), (amount, coins)
