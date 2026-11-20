import random

import pytest
from solution import group_aggregate


@pytest.mark.parametrize(
    "rows, keys, value, expected",
    [
        ([{"r": "eu", "v": 5}, {"r": None, "v": 1}, {"r": "eu"}, {"v": 7}], ["r"], "v", [(None, 2, 8, 1, 7), ("eu", 2, 5, 5, 5)]),
        ([], ["r"], "v", []),
        ([], [], "v", []),
        ([{"v": 1}, {"v": 2}], [], "v", [(2, 3, 1, 2)]),
        ([{"r": "a"}], ["r"], "v", [("a", 1, 0, None, None)]),
        ([{"r": "a", "v": None}, {"r": "a", "v": None}], ["r"], "v", [("a", 2, 0, None, None)]),
        ([{"r": "a", "v": -3}, {"r": "a", "v": 0}], ["r"], "v", [("a", 2, -3, -3, 0)]),
        ([{"r": "b", "v": 1}, {"r": "a", "v": 2}, {"r": "B", "v": 3}], ["r"], "v",
         [("B", 1, 3, 3, 3), ("a", 1, 2, 2, 2), ("b", 1, 1, 1, 1)]),
        ([{"x": 2, "y": "b", "v": 1}, {"x": 2, "y": None, "v": 2}, {"x": 1, "y": "z", "v": 3}, {"y": "a", "v": 4}, {"x": 2, "y": "a", "v": 5}],
         ["x", "y"], "v",
         [(None, "a", 1, 4, 4, 4), (1, "z", 1, 3, 3, 3), (2, None, 1, 2, 2, 2), (2, "a", 1, 5, 5, 5), (2, "b", 1, 1, 1, 1)]),
        ([{"k": 10, "v": 1}, {"k": 9, "v": 1}, {"k": -1, "v": 1}], ["k"], "v", [(-1, 1, 1, 1, 1), (9, 1, 1, 1, 1), (10, 1, 1, 1, 1)]),
        ([{"k": 1, "v": 10 ** 20}, {"k": 1, "v": 10 ** 20}], ["k"], "v", [(1, 2, 2 * 10 ** 20, 10 ** 20, 10 ** 20)]),
        ([{"k": 1, "v": 5}], ["k", "missing"], "v", [(1, None, 1, 5, 5, 5)]),
        ([{"k": 1, "v": 5}], ["k"], "k", [(1, 1, 1, 1, 1)]),
    ],
)
def test_examples(rows, keys, value, expected):
    assert [tuple(t) for t in group_aggregate(rows, keys, value)] == expected


def _oracle(rows, keys, value):
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r.get(k) for k in keys), []).append(r.get(value))
    out = []
    for g in sorted(groups, key=lambda t: [(x is not None, x if x is not None else 0) for x in t]):
        vals = [v for v in groups[g] if v is not None]
        out.append((*g, len(groups[g]), sum(vals), min(vals) if vals else None, max(vals) if vals else None))
    return out


def test_random_against_oracle():
    rng = random.Random(91)
    for _ in range(400):
        rows = []
        for _ in range(rng.randint(0, 15)):
            r = {}
            if rng.random() < 0.85:
                r["a"] = rng.choice([None, 1, 2, 3])
            if rng.random() < 0.85:
                r["b"] = rng.choice([None, "x", "y"])
            if rng.random() < 0.8:
                r["v"] = rng.choice([None, -2, 0, 5, 9])
            rows.append(r)
        keys = rng.choice([["a"], ["b"], ["a", "b"], ["b", "a"], []])
        assert [tuple(t) for t in group_aggregate(rows, keys, "v")] == _oracle(rows, keys, "v"), (rows, keys)
