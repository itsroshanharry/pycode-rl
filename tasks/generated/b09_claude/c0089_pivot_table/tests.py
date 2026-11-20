import random

import pytest
from solution import pivot_table

T = [("east", "Q1", 5), ("west", "Q1", 3), ("east", "Q2", 2), ("east", "Q1", 1)]


def _oracle(triples, policy, default, totals):
    groups = {}
    for r, c, v in triples:
        groups.setdefault((r, c), []).append(v)
    if policy == "error" and any(len(v) > 1 for v in groups.values()):
        raise ValueError
    pick = {"sum": sum, "max": max, "first": lambda v: v[0], "last": lambda v: v[-1], "error": lambda v: v[0]}[policy]
    cells = {k: pick(v) for k, v in groups.items()}
    rows, cols = sorted({k[0] for k in cells}), sorted({k[1] for k in cells})
    out = [[""] + cols + (["Total"] if totals else [])]
    for r in rows:
        vals = [cells.get((r, c), default) for c in cols]
        out.append([r] + vals + ([sum(cells.get((r, c), 0) for c in cols)] if totals else []))
    if totals:
        ct = [sum(cells.get((r, c), 0) for r in rows) for c in cols]
        out.append(["Total"] + ct + [sum(ct)])
    return out


CASES = [
    (T, "sum", -1, True), (T, "max", 0, False), (T, "first", 0, True), (T, "last", 0, True),
    ([], "sum", 7, False), ([], "sum", 7, True),
    ([("b", "y", 1), ("a", "x", 2)], "error", 9, True),
    ([("r", "B", 1), ("r", "a", 1), ("R", "b", 1)], "sum", 0, False),
    ([("x", "c", -5), ("x", "c", -2)], "max", 100, True),
    ([("r1", "c1", 1), ("r2", "c2", 2)], "sum", 1000, True),
    ([("r", "c", 0), ("r", "c", 0)], "sum", 5, True),
    ([("10", "a", 1), ("9", "a", 1), ("100", "a", 1)], "sum", 0, False),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], [["", "Q1", "Q2", "Total"], ["east", 6, 2, 8], ["west", 3, -1, 3], ["Total", 9, 2, 11]]),
    (CASES[5], [["", "Total"], ["Total", 0]]),
    (CASES[9], [["", "c1", "c2", "Total"], ["r1", 1, 1000, 1], ["r2", 1000, 2, 2], ["Total", 1, 2, 3]]),
    (CASES[11], [["", "a"], ["10", 1], ["100", 1], ["9", 1]]),
]


@pytest.mark.parametrize("args", CASES)
def test_against_oracle(args):
    assert [list(r) for r in pivot_table(*args)] == _oracle(*args)


@pytest.mark.parametrize("args, expected", FIXED)
def test_fixed(args, expected):
    assert [list(r) for r in pivot_table(*args)] == expected


@pytest.mark.parametrize("args", [(T, "error", 0, False), (T, "mean", 0, False), (T, "SUM", 0, False)])
def test_invalid(args):
    with pytest.raises(ValueError):
        pivot_table(*args)


def test_random_against_oracle():
    rng = random.Random(95)
    for _ in range(400):
        triples = [(rng.choice("abc"), rng.choice(["x", "y", "Z"]), rng.randint(-3, 5)) for _ in range(rng.randint(0, 8))]
        args = (triples, rng.choice(["sum", "max", "first", "last"]), rng.choice([0, -1, 9]), rng.random() < 0.5)
        assert [list(r) for r in pivot_table(*args)] == _oracle(*args), args
