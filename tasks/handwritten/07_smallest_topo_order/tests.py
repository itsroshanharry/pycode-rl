import random

import pytest
from solution import smallest_topo_order


@pytest.mark.parametrize(
    "n, edges, expected",
    [
        (4, [(2, 0), (1, 0), (3, 2)], [1, 3, 2, 0]),
        (2, [(0, 1), (1, 0)], []),
        (0, [], []),
        (1, [], [0]),
        (3, [], [0, 1, 2]),
        (3, [(0, 1)], [0, 1, 2]),
        (3, [(2, 1), (1, 0)], [2, 1, 0]),
        (3, [(0, 0)], []),
        (5, [(4, 3), (4, 3), (3, 1)], [0, 2, 4, 3, 1]),
        (6, [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)], [4, 5, 0, 2, 3, 1]),
        (4, [(0, 1), (1, 2), (2, 1), (3, 0)], []),
        (1000, [(i + 1, i) for i in range(999)], list(range(999, -1, -1))),
    ],
)
def test_examples(n, edges, expected):
    assert list(smallest_topo_order(n, edges)) == expected


def _oracle(n, edges):
    # O(n^2): repeatedly take the smallest node with no remaining incoming edge.
    remaining = set(range(n))
    pending = list(edges)
    order = []
    while remaining:
        blocked = {v for u, v in pending if u in remaining}
        free = sorted(remaining - blocked)
        if not free:
            return []
        u = free[0]
        order.append(u)
        remaining.discard(u)
    return order


def test_random_against_oracle():
    rng = random.Random(99)
    for _ in range(120):
        n = rng.randint(0, 9)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 14))] if n else []
        if rng.random() < 0.6:  # mostly DAGs: keep only forward edges in a random order
            perm = list(range(n)); rng.shuffle(perm); rank = {v: i for i, v in enumerate(perm)}
            edges = [(u, v) for u, v in edges if rank[u] < rank[v]]
        assert list(smallest_topo_order(n, edges)) == _oracle(n, edges), (n, edges)
