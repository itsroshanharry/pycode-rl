import random

import pytest
from solution import retry_delays


@pytest.mark.parametrize(
    "args, expected",
    [
        ((100, 2, 1000, [0, 10, -10], 6, 10 ** 9), [100, 220, 360, 800, 1100, 900]),
        ((100, 2, 1000, [], 0, 10 ** 9), []),
        ((100, 2, 1000, [], 5, 10 ** 9), [100, 200, 400, 800, 1000]),
        ((100, 1, 1000, [], 3, 10 ** 9), [100, 100, 100]),
        ((5000, 2, 1000, [], 2, 10 ** 9), [1000, 1000]),
        ((100, 2, 1000, [50], 5, 10 ** 9), [150, 300, 600, 1200, 1500]),
        ((100, 2, 1000, [-50], 3, 10 ** 9), [50, 100, 200]),
        ((7, 3, 1000, [-33], 3, 10 ** 9), [4, 14, 42]),
        ((100, 2, 1000, [], 5, 700), [100, 200, 400]),
        ((100, 2, 1000, [], 5, 699), [100, 200]),
        ((100, 2, 1000, [], 5, 99), []),
        ((100, 2, 1000, [], 5, 100), [100]),
        ((100, 2, 1000, [], 5, 0), []),
        ((1, 10, 10 ** 6, [], 9, 10 ** 12), [1, 10, 100, 1000, 10000, 100000, 1000000, 1000000, 1000000]),
        ((100, 2, 1000, [10, 0], 4, 10 ** 9), [110, 200, 440, 800]),
    ],
)
def test_examples(args, expected):
    assert list(retry_delays(*args)) == expected


def test_many_attempts_with_huge_factor():
    got = list(retry_delays(1, 10 ** 6, 5000, [1], 1000, 10 ** 12))
    assert got == [1] + [5050] * 999


@pytest.mark.parametrize(
    "args",
    [(0, 2, 10, [], 1, 1), (1, 0, 10, [], 1, 1), (1, 2, 0, [], 1, 1), (1, 2, 10, [51], 1, 1), (1, 2, 10, [-51], 1, 1),
     (1, 2, 10, [], -1, 1), (1, 2, 10, [], 1001, 1), (1, 2, 10, [], 1, -1)],
)
def test_invalid(args):
    with pytest.raises(ValueError):
        retry_delays(*args)


def _oracle(base, factor, cap, jit, n, budget):
    out, total = [], 0
    for k in range(n):
        raw = min(cap, base * factor ** k)
        d = raw * (100 + (jit[k % len(jit)] if jit else 0)) // 100
        if total + d > budget:
            break
        out.append(d)
        total += d
    return out


def test_random_against_oracle():
    rng = random.Random(59)
    for _ in range(400):
        args = (rng.randint(1, 500), rng.randint(1, 4), rng.randint(1, 5000),
                [rng.randint(-50, 50) for _ in range(rng.randint(0, 4))], rng.randint(0, 12), rng.randint(0, 20000))
        assert list(retry_delays(*args)) == _oracle(*args), args
