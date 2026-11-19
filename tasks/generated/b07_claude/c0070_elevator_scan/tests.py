import random

import pytest
from solution import elevator_scan


@pytest.mark.parametrize(
    "start, direction, requests, top, expected",
    [
        (5, "up", [7, 2, 9], 10, ([7, 9, 2], 13)),
        (5, "up", [2], 10, ([2], 13)),
        (5, "up", [], 10, ([], 0)),
        (5, "up", [5], 10, ([5], 0)),
        (5, "up", [5, 5, 7], 10, ([5, 7], 2)),
        (5, "up", [7, 9], 10, ([7, 9], 4)),
        (5, "down", [7, 2, 9], 10, ([2, 7, 9], 14)),
        (5, "down", [9], 10, ([9], 14)),
        (5, "down", [3, 1], 10, ([3, 1], 4)),
        (5, "up", [1, 3, 8, 8, 10], 10, ([8, 10, 3, 1], 14)),
        (0, "down", [4, 2], 10, ([2, 4], 4)),
        (10, "up", [4, 2], 10, ([4, 2], 8)),
        (0, "up", [0, 3], 10, ([0, 3], 3)),
        (3, "up", [3, 0], 3, ([3, 0], 3)),
        (0, "up", [], 0, ([], 0)),
        (0, "up", [0], 0, ([0], 0)),
        (4, "down", [5, 0, 4, 6], 6, ([4, 0, 5, 6], 10)),
    ],
)
def test_examples(start, direction, requests, top, expected):
    order, dist = elevator_scan(start, direction, requests, top)
    assert (list(order), dist) == expected


@pytest.mark.parametrize(
    "start, direction, requests, top",
    [(5, "left", [1], 10), (5, "UP", [1], 10), (5, "up", [11], 10), (5, "up", [-1], 10), (11, "up", [], 10), (0, "up", [], -1)],
)
def test_invalid(start, direction, requests, top):
    with pytest.raises(ValueError):
        elevator_scan(start, direction, requests, top)


def _simulate(start, direction, requests, top):
    pending, pos, step, order, dist = set(requests), start, 1 if direction == "up" else -1, [], 0
    while True:
        if pos in pending:
            pending.discard(pos)
            order.append(pos)
        if not pending:
            return order, dist
        if (step == 1 and pos == top) or (step == -1 and pos == 0):
            step = -step
        pos += step
        dist += 1


def test_random_against_simulation():
    rng = random.Random(57)
    for _ in range(400):
        top = rng.randint(0, 15)
        start = rng.randint(0, top)
        reqs = [rng.randint(0, top) for _ in range(rng.randint(0, 6))]
        d = rng.choice(["up", "down"])
        order, dist = elevator_scan(start, d, reqs, top)
        assert (list(order), dist) == _simulate(start, d, reqs, top), (start, d, reqs, top)
