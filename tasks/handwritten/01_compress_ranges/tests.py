import random

import pytest
from solution import compress_ranges


@pytest.mark.parametrize(
    "nums, expected",
    [
        ([5, 1, 2, 3, 3, 9, 10], "1..3,5,9,10"),
        ([-2, -1, 0, 4], "-2..0,4"),
        ([], ""),
        ([7], "7"),
        ([1, 2], "1,2"),
        ([3, 2, 1], "1..3"),
        ([1, 1, 1], "1"),
        ([0, 2, 4], "0,2,4"),
        ([10, 11, 12, 14, 15, 16, 17, 20], "10..12,14..17,20"),
        ([-5, -4, -3, -1, 0, 1], "-5..-3,-1..1"),
        ([100, 99, 98, 50, 51], "50,51,98..100"),
        ([4, 4, 5, 5, 6, 6, 8, 8], "4..6,8"),
        (list(range(-1000, 1001)) + [5000], "-1000..1000,5000"),
    ],
)
def test_examples(nums, expected):
    assert compress_ranges(nums) == expected


def _oracle(nums):
    # Independent formulation: mark membership, scan the whole span once.
    if not nums:
        return ""
    present = set(nums)
    parts, lo, hi = [], min(present), max(present)
    x = lo
    while x <= hi:
        if x not in present:
            x += 1
            continue
        start = x
        while x + 1 in present:
            x += 1
        run = list(range(start, x + 1))
        parts += [f"{start}..{x}"] if len(run) >= 3 else [str(v) for v in run]
        x += 1
    return ",".join(parts)


def test_random_against_oracle():
    rng = random.Random(1234)
    for _ in range(150):
        nums = [rng.randint(-15, 15) for _ in range(rng.randint(0, 25))]
        assert compress_ranges(nums) == _oracle(nums), nums
