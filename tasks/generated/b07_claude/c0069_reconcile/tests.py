import random

import pytest
from solution import reconcile


def _norm(r):
    m, ua, ub = r
    return [tuple(x) for x in m], list(ua), list(ub)


@pytest.mark.parametrize(
    "a, b, tol, expected",
    [
        ([(1, 10, 500), (2, 10, 500)], [(101, 9, 500), (102, 10, 500), (103, 30, 500)], 1, ([(1, 102), (2, 101)], [], [103])),
        ([], [], 0, ([], [], [])),
        ([(1, 0, 5)], [], 3, ([], [1], [])),
        ([], [(9, 0, 5)], 3, ([], [], [9])),
        ([(1, 10, 500)], [(101, 8, 500), (102, 12, 500)], 2, ([(1, 101)], [], [102])),
        ([(1, 10, 500)], [(102, 12, 500), (101, 8, 500)], 2, ([(1, 101)], [], [102])),
        ([(1, 10, 500)], [(101, 10, 501)], 5, ([], [1], [101])),
        ([(1, 10, 5)], [(101, 11, 5)], 0, ([], [1], [101])),
        ([(1, 10, 5)], [(101, 11, 5)], 1, ([(1, 101)], [], [])),
        ([(1, 10, 5)], [(101, 9, 5), (102, 9, 5)], 3, ([(1, 101)], [], [102])),
        ([(1, 10, 5)], [(101, 11, 5), (102, 11, 5)], 3, ([(1, 101)], [], [102])),
        ([(1, 10, 5), (2, 8, 5)], [(101, 9, 5)], 1, ([(1, 101)], [2], [])),
        ([(1, 10, 5)], [(101, 7, 5), (102, 12, 5)], 3, ([(1, 102)], [], [101])),
        ([(1, -5, -20)], [(101, -3, -20), (102, -7, -20)], 2, ([(1, 102)], [], [101])),
        ([(1, 10, 5), (1, 10, 5)], [(7, 10, 5), (7, 10, 5)], 0, ([(1, 7), (1, 7)], [], [])),
        ([(1, 10, 5), (2, 10, 6)], [(101, 10, 6), (102, 10, 5)], 0, ([(1, 102), (2, 101)], [], [])),
        ([(1, 5, 5), (2, 5, 5), (3, 5, 5)], [(101, 3, 5), (102, 7, 5), (103, 5, 5)], 2,
         ([(1, 103), (2, 101), (3, 102)], [], [])),
    ],
)
def test_examples(a, b, tol, expected):
    assert _norm(reconcile(a, b, tol)) == expected


def test_invalid():
    with pytest.raises(ValueError):
        reconcile([], [], -1)


def _brute(a, b, tol):
    used, matches, ua = set(), [], []
    for aid, day, amt in a:
        cands = [(abs(bd - day), bd, j) for j, (_, bd, ba) in enumerate(b) if j not in used and ba == amt and abs(bd - day) <= tol]
        if cands:
            _, _, j = min(cands)
            used.add(j)
            matches.append((aid, b[j][0]))
        else:
            ua.append(aid)
    return matches, ua, [b[j][0] for j in range(len(b)) if j not in used]


def test_random_against_brute_force():
    rng = random.Random(96)
    for _ in range(300):
        a = [(i, rng.randint(0, 30), rng.choice([5, 7])) for i in range(rng.randint(0, 15))]
        b = [(100 + j, rng.randint(0, 30), rng.choice([5, 7])) for j in range(rng.randint(0, 15))]
        tol = rng.randint(0, 6)
        assert _norm(reconcile(a, b, tol)) == _brute(a, b, tol), (a, b, tol)


def test_large_single_amount():
    # 20 000 x 20 000 entries, one amount: an all-pairs scan is ~4e8 steps.
    n = 20000
    rng = random.Random(1996)
    a = [(i, i * 10, 777) for i in range(n)]
    b = [(100000 + i, i * 10 + 3, 777) for i in range(n)]
    rng.shuffle(b)
    m, ua, ub = _norm(reconcile(a, b, 5))
    assert m == [(i, 100000 + i) for i in range(n)]
    assert ua == [] and ub == []
