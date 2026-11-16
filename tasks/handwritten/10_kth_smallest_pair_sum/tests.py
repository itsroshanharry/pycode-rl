import random

import pytest
from solution import kth_smallest_pair_sum


@pytest.mark.parametrize(
    "a, b, k, expected",
    [
        ([1, 7, 11], [2, 4, 6], 3, 7),
        ([3, 1], [1, 1], 4, 4),
        ([5], [5], 1, 10),
        ([-3, -1], [-2, 0], 1, -5),
        ([-3, -1], [-2, 0], 2, -3),
        ([-3, -1], [-2, 0], 3, -3),
        ([-3, -1], [-2, 0], 4, -1),
        ([2, 2, 2], [3, 3], 6, 5),
        ([10**9, -(10**9)], [10**9], 2, 2 * 10**9),
        ([9, 1, 5], [0], 2, 5),
        (list(range(2000)), list(range(2000)), 1, 0),
        (list(range(2000)), list(range(2000)), 4_000_000, 3998),
        (list(range(2000)), list(range(2000)), 2_000_000, 1999),
    ],
)
def test_examples(a, b, k, expected):
    assert kth_smallest_pair_sum(a, b, k) == expected


@pytest.mark.parametrize("a, b, k", [([], [1], 1), ([1], [], 1), ([1], [1], 0), ([1], [1], 2), ([1, 2], [3], -1)])
def test_out_of_range(a, b, k):
    with pytest.raises(ValueError):
        kth_smallest_pair_sum(a, b, k)


def test_random_against_brute_force():
    rng = random.Random(31)
    for _ in range(150):
        a = [rng.randint(-20, 20) for _ in range(rng.randint(1, 8))]
        b = [rng.randint(-20, 20) for _ in range(rng.randint(1, 8))]
        sums = sorted(x + y for x in a for y in b)
        k = rng.randint(1, len(sums))
        assert kth_smallest_pair_sum(a, b, k) == sums[k - 1], (a, b, k)
