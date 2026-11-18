import random

import pytest
from solution import stableford_points


@pytest.mark.parametrize(
    "strokes, pars, si, handicap, expected",
    [
        ([5, 3, 7], [4, 3, 5], [2, 3, 1], 2, 5),
        ([0, 2, 4], [4, 3, 4], [1, 2, 3], 4, 7),
        ([3], [3], [1], 0, 2),
        ([1], [3], [1], 0, 4),
        ([9], [4], [1], 0, 0),
        ([2], [5], [1], 0, 5),
        ([0], [5], [1], 10, 0),
        ([5, 5], [4, 4], [1, 2], 2, 4),
        ([5, 5], [4, 4], [2, 1], 1, 3),
        ([7] * 18, [4] * 18, list(range(1, 19)), 54, 36),
        ([4] * 18, [4] * 18, list(range(18, 0, -1)), 18, 54),
        ([4] * 18, [4] * 18, list(range(1, 19)), 19, 55),
        ([6, 4, 3, 5], [5, 4, 3, 4], [4, 1, 3, 2], 6, 12),
        ([10, 10], [3, 3], [1, 2], 0, 0),
    ],
)
def test_examples(strokes, pars, si, handicap, expected):
    assert stableford_points(strokes, pars, si, handicap) == expected


@pytest.mark.parametrize(
    "strokes, pars, si, handicap",
    [
        ([4, 4], [4], [1, 2], 0),
        ([], [], [], 0),
        ([4] * 19, [4] * 19, list(range(1, 20)), 0),
        ([4, 4], [4, 4], [1, 1], 0),
        ([4, 4], [4, 4], [0, 1], 0),
        ([4], [2], [1], 0),
        ([4], [7], [1], 0),
        ([-1], [4], [1], 0),
        ([4], [4], [1], -1),
    ],
)
def test_invalid(strokes, pars, si, handicap):
    with pytest.raises(ValueError):
        stableford_points(strokes, pars, si, handicap)


def _oracle(strokes, pars, si, handicap):
    # Hand out handicap strokes one at a time, round-robin in stroke-index order.
    n = len(strokes)
    received = [0] * n
    hole_for_index = {s: i for i, s in enumerate(si)}
    for k in range(handicap):
        received[hole_for_index[k % n + 1]] += 1
    pts = 0
    for i in range(n):
        if strokes[i]:
            pts += max(0, 2 + pars[i] - (strokes[i] - received[i]))
    return pts


def test_random_against_oracle():
    rng = random.Random(66)
    for _ in range(200):
        n = rng.randint(1, 18)
        pars = [rng.randint(3, 6) for _ in range(n)]
        strokes = [rng.choice([0, rng.randint(1, 10)]) for _ in range(n)]
        si = rng.sample(range(1, n + 1), n)
        h = rng.randint(0, 54)
        assert stableford_points(strokes, pars, si, h) == _oracle(strokes, pars, si, h), (strokes, pars, si, h)
