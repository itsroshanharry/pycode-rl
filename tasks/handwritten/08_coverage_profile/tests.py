import random

import pytest
from solution import coverage_profile


def _norm(segments):
    return [tuple(s) for s in segments]


@pytest.mark.parametrize(
    "intervals, expected",
    [
        ([(0, 5, 1), (3, 8, 2)], [(0, 3, 1), (3, 5, 3), (5, 8, 2)]),
        ([(0, 2, 1), (2, 4, 1)], [(0, 4, 1)]),
        ([], []),
        ([(0, 1, 0)], []),
        ([(0, 5, 1), (0, 5, -1)], []),
        ([(1, 4, 2)], [(1, 4, 2)]),
        ([(-5, -1, 3)], [(-5, -1, 3)]),
        ([(0, 10, 1), (2, 4, -1)], [(0, 2, 1), (4, 10, 1)]),
        ([(0, 3, 2), (3, 6, 1), (6, 9, 2)], [(0, 3, 2), (3, 6, 1), (6, 9, 2)]),
        ([(0, 4, 1), (1, 3, 1), (1, 3, -1)], [(0, 4, 1)]),
        ([(0, 2, -3), (1, 3, 1)], [(0, 1, -3), (1, 2, -2), (2, 3, 1)]),
        ([(5, 6, 1), (0, 1, 1)], [(0, 1, 1), (5, 6, 1)]),
        ([(0, 10**12, 7)], [(0, 10**12, 7)]),
    ],
)
def test_examples(intervals, expected):
    assert _norm(coverage_profile(intervals)) == expected


def _oracle(intervals):
    # Evaluate every unit cell [x, x+1) directly, then merge equal neighbours.
    if not intervals:
        return []
    lo = min(s for s, _, _ in intervals)
    hi = max(e for _, e, _ in intervals)
    out = []
    for x in range(lo, hi):
        w = sum(wt for s, e, wt in intervals if s <= x < e)
        if w == 0:
            continue
        if out and out[-1][1] == x and out[-1][2] == w:
            out[-1] = (out[-1][0], x + 1, w)
        else:
            out.append((x, x + 1, w))
    return out


def test_random_against_oracle():
    rng = random.Random(2024)
    for _ in range(150):
        intervals = []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(-10, 10)
            intervals.append((s, s + rng.randint(1, 8), rng.randint(-3, 3)))
        assert _norm(coverage_profile(intervals)) == _oracle(intervals), intervals
