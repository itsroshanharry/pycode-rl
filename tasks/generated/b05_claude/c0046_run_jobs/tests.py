import random

import pytest
from solution import run_jobs


@pytest.mark.parametrize(
    "jobs, aging, expected",
    [
        ([("x", 0, 1, 10), ("old", 1, 0, 3), ("new", 9, 3, 1)], 2, [("x", 0), ("old", 10), ("new", 13)]),
        ([("x", 0, 1, 10), ("old", 1, 0, 3), ("new", 9, 3, 1)], 100, [("x", 0), ("new", 10), ("old", 11)]),
        ([], 1, []),
        ([("a", 0, 1, 5), ("b", 1, 5, 2), ("c", 2, 1, 1)], 2, [("a", 0), ("b", 5), ("c", 7)]),
        ([("late", 7, 0, 2)], 3, [("late", 7)]),
        ([("a", 5, 0, 1), ("b", 20, 0, 1)], 1, [("a", 5), ("b", 20)]),
        # arrival exactly at the moment the worker frees up counts
        ([("a", 0, 0, 4), ("hi", 4, 9, 1), ("lo", 1, 0, 1)], 10, [("a", 0), ("hi", 4), ("lo", 5)]),
        # ties: earlier arrival wins, then list order
        ([("p", 0, 0, 3), ("q", 2, 1, 1), ("r", 1, 1, 1)], 100, [("p", 0), ("r", 3), ("q", 4)]),
        ([("p", 0, 0, 3), ("q", 1, 1, 1), ("r", 1, 1, 1)], 100, [("p", 0), ("q", 3), ("r", 4)]),
        ([("r", 1, 1, 1), ("q", 1, 1, 1), ("p", 0, 0, 3)], 100, [("p", 0), ("r", 3), ("q", 4)]),
        # aging is integer division of the wait so far: 5 // 3 = 1, not 1.67
        ([("w", 0, 0, 6), ("a", 1, 0, 1), ("b", 5, 1, 1)], 3, [("w", 0), ("a", 6), ("b", 7)]),
        ([("w", 0, 0, 6), ("a", 1, 0, 1), ("b", 6, 2, 1)], 3, [("w", 0), ("b", 6), ("a", 7)]),
        # negative priorities are fine
        ([("n", 0, -5, 2), ("m", 0, -3, 2)], 1, [("m", 0), ("n", 2)]),
        # equal priority, equal arrival, list order
        ([("b", 0, 0, 1), ("a", 0, 0, 1)], 1, [("b", 0), ("a", 1)]),
    ],
)
def test_examples(jobs, aging, expected):
    assert [tuple(x) for x in run_jobs(jobs, aging)] == expected


@pytest.mark.parametrize(
    "jobs, aging",
    [
        ([("a", 0, 0, 1)], 0),
        ([("a", 0, 0, 1)], -2),
        ([("a", -1, 0, 1)], 1),
        ([("a", 0, 0, 0)], 1),
        ([("a", 0, 0, 1), ("a", 3, 0, 1)], 1),
    ],
)
def test_invalid(jobs, aging):
    with pytest.raises(ValueError):
        run_jobs(jobs, aging)


def _oracle(jobs, aging):
    # tick the clock one unit at a time
    started, out, t, busy_until = set(), [], 0, 0
    while len(started) < len(jobs):
        if t >= busy_until:
            cands = [(j[2] + (t - j[1]) // aging, -j[1], -i, i) for i, j in enumerate(jobs) if i not in started and j[1] <= t]
            if cands:
                i = max(cands)[3]
                started.add(i)
                out.append((jobs[i][0], t))
                busy_until = t + jobs[i][3]
        t += 1
    return out


def test_random_against_oracle():
    rng = random.Random(54)
    for _ in range(200):
        n = rng.randint(1, 9)
        jobs = [(f"j{k}", rng.randint(0, 30), rng.randint(-2, 4), rng.randint(1, 6)) for k in range(n)]
        aging = rng.randint(1, 6)
        assert [tuple(x) for x in run_jobs(jobs, aging)] == _oracle(jobs, aging), (jobs, aging)
