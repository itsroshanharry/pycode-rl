import random
from bisect import bisect_right

import pytest
from solution import resolve_local

T = [(1000, 120), (5000, 60)]


@pytest.mark.parametrize(
    "local, expected",
    [
        (1059, [999]), (1060, []), (1100, []), (1119, []), (1120, [1000]), (3000, [2880]),
        (5059, [4939]), (5060, [4940, 5000]), (5100, [4980, 5040]), (5119, [4999, 5059]),
        (5120, [5060]), (0, [-60]), (-100000, [-100060]), (10 ** 9, [10 ** 9 - 60]),
    ],
)
def test_one_change_each_way(local, expected):
    assert [list(x) for x in resolve_local([local], 60, T)] == [expected]


def test_examples():
    got = resolve_local([1059, 1060, 1120, 5060, 5120], 60, [(1000, 120), (5000, 60)])
    assert [list(x) for x in got] == [[999], [], [1000], [4940, 5000], [5060]]


def test_no_transitions():
    assert [list(x) for x in resolve_local([0, 7, -3], -300, [])] == [[300], [307], [297]]


def test_empty_queries():
    assert list(resolve_local([], 0, T)) == []


def test_negative_offsets_and_day_skip():
    # -10:00 -> +14:00 (a whole day skipped), then back to -10:00 (a day repeated)
    trans = [(5000, 840), (20000, -600)]
    got = resolve_local([4399, 4400, 5839, 5840, 19399, 19400, 20839, 20840], -600, trans)
    assert [list(x) for x in got] == [[4999], [], [], [5000], [18559], [18560, 20000], [19999, 21439], [21440]]


def test_unchanged_offset_transition():
    got = resolve_local([999, 1000, 1001], 0, [(1000, 0)])
    assert [list(x) for x in got] == [[999], [1000], [1001]]


def test_queries_unsorted_and_repeated():
    got = resolve_local([5060, 1060, 5060, 999], 60, T)
    assert [list(x) for x in got] == [[4940, 5000], [], [4940, 5000], [939]]


def _brute(queries, base, trans):
    bounds = [None] + [at for at, _ in trans] + [None]
    offs = [base] + [o for _, o in trans]
    out = []
    for q in queries:
        res = []
        for k, off in enumerate(offs):
            u = q - off
            if (bounds[k] is None or bounds[k] <= u) and (bounds[k + 1] is None or u < bounds[k + 1]):
                res.append(u)
        out.append(sorted(res))
    return out


def _random_table(rng, n):
    trans, at = [], rng.randint(-10 ** 6, 10 ** 6)
    for _ in range(n):
        at += rng.randint(2881, 20000)
        trans.append((at, rng.randint(-1440, 1440)))
    return rng.randint(-1440, 1440), trans


def test_random_small_against_brute_force():
    rng = random.Random(6)
    for _ in range(200):
        base, trans = _random_table(rng, rng.randint(0, 6))
        pts = [at + d for at, _ in trans for d in (-3000, -1500, -1, 0, 1, 1500)] or [0]
        queries = [rng.choice(pts) + rng.randint(-1500, 1500) for _ in range(30)]
        assert [list(x) for x in resolve_local(queries, base, trans)] == _brute(queries, base, trans)


def test_large():
    # 20 000 transitions x 40 000 queries: checking every period per query is ~8e8 steps.
    rng = random.Random(60)
    base, trans = _random_table(rng, 20000)
    starts = [at for at, _ in trans]
    offs = [base] + [o for _, o in trans]
    queries = [rng.randint(starts[0] - 5000, starts[-1] + 5000) for _ in range(40000)]
    got = resolve_local(queries, base, trans)
    assert len(got) == len(queries)
    for q, res in zip(queries, got):
        res = list(res)
        assert res == sorted(res) and len(res) <= 2
        for u in res:
            assert u + offs[bisect_right(starts, u)] == q
        # completeness: every period that could hold a solution was considered
        expected = 0
        k = bisect_right(starts, q - 1440)
        for j in range(k, min(k + 3, len(offs))):
            u = q - offs[j]
            if bisect_right(starts, u) == j:
                expected += 1
        assert len(res) == expected
