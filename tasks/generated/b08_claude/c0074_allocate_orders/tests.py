import random

import pytest
from solution import allocate_orders


def _norm(res):
    return [(o, [tuple(t) for t in taken], short) for o, taken, short in res]


@pytest.mark.parametrize(
    "orders, warehouses, expected",
    [
        ([("o1", 1, "A", 5), ("o2", 9, "A", 4)], [("north", {"A": 3}), ("south", {"A": 3})],
         [("o1", [("south", 2)], 3), ("o2", [("north", 3), ("south", 1)], 0)]),
        ([], [("w", {"A": 1})], []),
        ([("o", 1, "A", 2)], [], [("o", [], 2)]),
        ([("o", 1, "B", 2)], [("w", {"A": 5})], [("o", [], 2)]),
        ([("o", 1, "A", 2)], [("w1", {"A": 0}), ("w2", {"A": 5})], [("o", [("w2", 2)], 0)]),
        ([("a", 5, "X", 2), ("b", 5, "X", 2)], [("w", {"X": 3})], [("a", [("w", 2)], 0), ("b", [("w", 1)], 1)]),
        ([("b", 5, "X", 2), ("a", 5, "X", 2)], [("w", {"X": 3})], [("b", [("w", 2)], 0), ("a", [("w", 1)], 1)]),
        ([("lo", -1, "X", 1), ("hi", 0, "X", 1)], [("w", {"X": 1})], [("lo", [], 1), ("hi", [("w", 1)], 0)]),
        ([("o1", 1, "A", 1), ("o2", 1, "B", 1)], [("w", {"A": 1, "B": 1})], [("o1", [("w", 1)], 0), ("o2", [("w", 1)], 0)]),
        ([("o", 1, "A", 10)], [("a", {"A": 2}), ("b", {"A": 3}), ("c", {"A": 4})], [("o", [("a", 2), ("b", 3), ("c", 4)], 1)]),
        ([("o", 1, "A", 5)], [("a", {"A": 2}), ("b", {"A": 3}), ("c", {"A": 4})], [("o", [("a", 2), ("b", 3)], 0)]),
        ([("x", 3, "S", 2), ("y", 7, "S", 2), ("z", 5, "S", 2)], [("w", {"S": 3})],
         [("x", [], 2), ("y", [("w", 2)], 0), ("z", [("w", 1)], 1)]),
    ],
)
def test_examples(orders, warehouses, expected):
    assert _norm(allocate_orders(orders, warehouses)) == expected


@pytest.mark.parametrize(
    "orders, warehouses",
    [
        ([("o", 1, "A", 0)], [("w", {"A": 1})]),
        ([("o", 1, "A", 1), ("o", 2, "A", 1)], [("w", {"A": 1})]),
        ([("o", 1, "A", 1)], [("w", {"A": 1}), ("w", {"A": 1})]),
        ([("o", 1, "A", 1)], [("w", {"A": -1})]),
    ],
)
def test_invalid(orders, warehouses):
    with pytest.raises(ValueError):
        allocate_orders(orders, warehouses)


def _oracle(orders, warehouses):
    stock = {(w, s): q for w, lv in warehouses for s, q in lv.items()}
    names = [w for w, _ in warehouses]
    done = {}
    for prio in sorted({o[1] for o in orders}, reverse=True):
        for oid, p, sku, qty in orders:
            if p != prio:
                continue
            got = []
            for w in names:
                t = min(qty, stock.get((w, sku), 0))
                if t:
                    stock[(w, sku)] -= t
                    qty -= t
                    got.append((w, t))
            done[oid] = (oid, got, qty)
    return [done[o[0]] for o in orders]


def test_random_against_oracle():
    rng = random.Random(46)
    for _ in range(300):
        orders = [(f"o{i}", rng.randint(0, 3), rng.choice("AB"), rng.randint(1, 5)) for i in range(rng.randint(0, 8))]
        warehouses = [(f"w{k}", {s: rng.randint(0, 4) for s in rng.sample("ABC", rng.randint(0, 3))}) for k in range(rng.randint(0, 3))]
        assert _norm(allocate_orders(orders, warehouses)) == _oracle(orders, warehouses)
