import random

import pytest
from solution import rate_limit


@pytest.mark.parametrize(
    "requests, window, limit, expected",
    [
        ([("a", 0), ("a", 1), ("a", 2), ("b", 2), ("a", 10)], 10, 2, [True, True, False, True, True]),
        ([], 5, 1, []),
        ([("a", 0), ("a", 0), ("a", 0)], 1, 2, [True, True, False]),
        ([("a", 0), ("a", 1)], 1, 1, [True, True]),
        ([("a", 0), ("a", 4), ("a", 5)], 5, 1, [True, False, True]),
        ([("a", 0), ("a", 3), ("a", 6), ("a", 9)], 5, 1, [True, False, True, False]),
        ([("x", 1), ("y", 1), ("x", 1), ("y", 1)], 100, 1, [True, True, False, False]),
        ([("a", 0), ("a", 1), ("a", 2), ("a", 3), ("a", 4), ("a", 5)], 3, 2, [True, True, False, True, True, False]),
        ([("a", -5), ("a", -4), ("a", 0)], 5, 1, [True, False, True]),
    ],
)
def test_examples(requests, window, limit, expected):
    assert list(rate_limit(requests, window, limit)) == expected


@pytest.mark.parametrize("requests, window, limit", [([("a", 1)], 0, 1), ([("a", 1)], 1, 0), ([("a", 5), ("b", 4)], 3, 1)])
def test_invalid(requests, window, limit):
    with pytest.raises(ValueError):
        rate_limit(requests, window, limit)


def _oracle(requests, window, limit):
    hist, out = {}, []
    for c, t in requests:
        ok = sum(1 for x in hist.get(c, []) if t - window < x <= t) < limit
        if ok:
            hist.setdefault(c, []).append(t)
        out.append(ok)
    return out


def test_random_against_oracle():
    rng = random.Random(56)
    for _ in range(200):
        t, reqs = 0, []
        for _ in range(rng.randint(0, 30)):
            t += rng.choice([0, 0, 1, 2, 7])
            reqs.append((rng.choice("abc"), t))
        w, lim = rng.randint(1, 10), rng.randint(1, 4)
        assert list(rate_limit(reqs, w, lim)) == _oracle(reqs, w, lim), (reqs, w, lim)


def test_large_single_client():
    reqs = [("c", i // 3) for i in range(30_000)]
    out = list(rate_limit(reqs, 10**9, 30_000))
    assert out == [True] * 30_000


def test_large_mixed():
    rng = random.Random(9)
    t, reqs = 0, []
    for _ in range(30_000):
        t += rng.choice([0, 1])
        reqs.append((rng.choice(["a", "b", "c", "d"]), t))
    out = list(rate_limit(reqs, 50, 20))
    # Cheap independent check: no client exceeds the limit inside any window of allowed times.
    by_client = {}
    for (c, tt), ok in zip(reqs, out):
        if ok:
            by_client.setdefault(c, []).append(tt)
    for times in by_client.values():
        assert all(times[i + 20] - times[i] >= 50 for i in range(len(times) - 20))
    assert sum(out) > 0
