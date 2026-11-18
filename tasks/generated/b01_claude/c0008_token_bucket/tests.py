import random

import pytest
from solution import token_bucket


@pytest.mark.parametrize(
    "capacity, rate, requests, expected",
    [
        (2, 1, [(0, 1), (0, 1), (0, 1), (1000, 1)], [True, True, False, True]),
        (5, 2, [(0, 5), (1500, 3), (1600, 1)], [True, True, False]),
        (1, 0, [(0, 1), (5000, 1)], [True, False]),
        (3, 1, [(0, 4)], [False]),
        (3, 1, [], []),
        (10, 1, [(0, 10), (500, 1), (1000, 1)], [True, False, True]),
        (2, 3, [(0, 2), (333, 1), (334, 1)], [True, False, True]),
        (2, 1, [(0, 2), (10000, 1), (10000, 1), (10000, 1)], [True, True, True, False]),
        (1, 1, [(0, 1), (0, 1)], [True, False]),
        (1, 1, [(0, 1)] + [(100 * k, 1) for k in range(1, 11)], [True] + [False] * 9 + [True]),
        (100, 7, [(0, 100), (10**9, 100)], [True, True]),
    ],
)
def test_examples(capacity, rate, requests, expected):
    assert list(token_bucket(capacity, rate, requests)) == expected


@pytest.mark.parametrize(
    "capacity, rate, requests",
    [
        (5, 1, [(10, 1), (5, 1)]),
        (5, 1, [(-1, 1)]),
        (5, 1, [(0, 0)]),
        (0, 1, [(0, 1)]),
        (5, -1, [(0, 1)]),
    ],
)
def test_invalid(capacity, rate, requests):
    with pytest.raises(ValueError):
        token_bucket(capacity, rate, requests)


def _oracle(capacity, rate, requests):
    # Integer milli-tokens: `rate` tokens/s is exactly `rate` milli-tokens per ms.
    level, last, out = capacity * 1000, 0, []
    for t, cost in requests:
        level = min(capacity * 1000, level + rate * (t - last))
        last = t
        ok = level >= cost * 1000
        if ok:
            level -= cost * 1000
        out.append(ok)
    return out


def test_random_against_oracle():
    rng = random.Random(55)
    for _ in range(200):
        cap, rate = rng.randint(1, 6), rng.randint(0, 5)
        t, reqs = 0, []
        for _ in range(rng.randint(0, 25)):
            t += rng.choice([0, rng.randint(1, 400), rng.randint(1, 3000)])
            reqs.append((t, rng.randint(1, 4)))
        assert list(token_bucket(cap, rate, reqs)) == _oracle(cap, rate, reqs), (cap, rate, reqs)
