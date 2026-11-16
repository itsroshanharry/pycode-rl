import random

import pytest
from solution import lru_trace


@pytest.mark.parametrize(
    "capacity, ops, expected",
    [
        (2, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("get", 3)], [1, -1, 3]),
        (0, [("put", 1, 1), ("get", 1)], [-1]),
        (2, [("put", 1, 1), ("put", 2, 2), ("put", 1, 10), ("put", 3, 3), ("get", 1), ("get", 2), ("get", 3)], [10, -1, 3]),
        (2, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("get", 1)], [1, -1, 1]),
        (2, [("put", 1, 1), ("put", 2, 2), ("get", 9), ("put", 3, 3), ("get", 1), ("get", 2)], [-1, -1, 2]),
        (1, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("get", 2)], [-1, 2]),
        (3, [("put", 1, 1), ("put", 2, 2)], []),
        (3, [("put", 5, 0), ("get", 5), ("put", 6, -7), ("get", 6)], [0, -7]),
        (2, [], []),
    ],
)
def test_examples(capacity, ops, expected):
    assert list(lru_trace(capacity, ops)) == expected


def _oracle(capacity, ops):
    # List ordered from least to most recently used.
    order, store, out = [], {}, []
    for op in ops:
        if op[0] == "get":
            if op[1] in store:
                order.remove(op[1]); order.append(op[1]); out.append(store[op[1]])
            else:
                out.append(-1)
        elif capacity > 0:
            k, v = op[1], op[2]
            if k in store:
                order.remove(k)
            elif len(order) == capacity:
                del store[order.pop(0)]
            order.append(k); store[k] = v
    return out


def test_random_against_oracle():
    rng = random.Random(7)
    for _ in range(100):
        cap = rng.randint(0, 4)
        ops = [("get", rng.randint(0, 6)) if rng.random() < 0.4 else ("put", rng.randint(0, 6), rng.randint(-50, 50))
               for _ in range(rng.randint(0, 40))]
        assert list(lru_trace(cap, ops)) == _oracle(cap, ops), (cap, ops)
