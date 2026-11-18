import functools
import random

import pytest
from solution import top_k_per_group


@pytest.mark.parametrize(
    "rows, k, expected",
    [
        ([("a", "x", 5), ("b", "y", 1), ("a", "w", 5), ("a", "z", 9)], 2, [("a", ["z", "w"]), ("b", ["y"])]),
        ([], 3, []),
        ([("g", "n", 1)], 0, [("g", [])]),
        ([("g", "b", 2), ("g", "a", 2), ("g", "c", 3)], 5, [("g", ["c", "a", "b"])]),
        ([("g", "a", 1), ("g", "a", 1), ("g", "a", 1)], 2, [("g", ["a", "a"])]),
        ([("g", "B", 4), ("g", "a", 4)], 2, [("g", ["B", "a"])]),
        ([("z", "p", 1), ("y", "q", 2), ("z", "r", 3)], 1, [("z", ["r"]), ("y", ["q"])]),
        ([("g", "low", -5), ("g", "zero", 0), ("g", "neg", -1)], 2, [("g", ["zero", "neg"])]),
        ([("g", "x", 10**12), ("g", "y", 10**12 - 1)], 1, [("g", ["x"])]),
        ([("A", "n", 1), ("a", "m", 1)], 1, [("A", ["n"]), ("a", ["m"])]),
    ],
)
def test_examples(rows, k, expected):
    assert list(top_k_per_group(rows, k).items()) == expected


def test_negative_k():
    with pytest.raises(ValueError):
        top_k_per_group([("a", "b", 1)], -1)


def _cmp(x, y):
    (_, nx, sx), (_, ny, sy) = x, y
    if sx != sy:
        return -1 if sx > sy else 1
    return (nx > ny) - (nx < ny)


def _oracle(rows, k):
    out = {}
    for g in dict.fromkeys(r[0] for r in rows):
        members = [r for r in rows if r[0] == g]
        out[g] = [r[1] for r in sorted(members, key=functools.cmp_to_key(_cmp))][:k]
    return out


def test_random_against_oracle():
    rng = random.Random(94)
    for _ in range(200):
        rows = [(rng.choice("abc"), rng.choice(["x", "y", "Y", "z", "w"]), rng.randint(-3, 3)) for _ in range(rng.randint(0, 20))]
        k = rng.randint(0, 5)
        assert list(top_k_per_group(rows, k).items()) == list(_oracle(rows, k).items()), (rows, k)
