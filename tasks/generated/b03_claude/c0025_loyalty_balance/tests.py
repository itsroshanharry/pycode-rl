import random

import pytest
from solution import loyalty_balance


@pytest.mark.parametrize(
    "events, expiry, expected",
    [
        ([(0, "earn", 100), (5, "earn", 50), (10, "redeem", 120), (30, "earn", 10), (31, "redeem", 20)], 30, [100, 150, 30, 40, 20]),
        ([], 5, []),
        ([(0, "earn", 10), (4, "redeem", 10)], 5, [10, 0]),
        ([(0, "earn", 10), (5, "redeem", 10)], 5, [10, 0]),
        ([(0, "earn", 10), (4, "earn", 1), (5, "redeem", 1)], 5, [10, 11, 0]),
        ([(0, "earn", 10), (1, "redeem", 11)], 5, [10, 10]),
        ([(0, "earn", 5), (0, "redeem", 5), (0, "earn", 3)], 1, [5, 0, 3]),
        ([(0, "earn", 5), (1, "redeem", 1)], 1, [5, 0]),
        ([(0, "earn", 10), (3, "earn", 10), (4, "redeem", 15), (6, "redeem", 1)], 5, [10, 20, 5, 4]),
        ([(0, "earn", 10), (3, "earn", 10), (4, "redeem", 15), (8, "redeem", 1)], 5, [10, 20, 5, 0]),
        ([(2, "redeem", 1)], 3, [0]),
        ([(0, "earn", 7), (2, "earn", 7), (2, "earn", 7), (3, "redeem", 14), (100, "earn", 1)], 10, [7, 14, 21, 7, 1]),
    ],
)
def test_examples(events, expiry, expected):
    assert list(loyalty_balance(events, expiry)) == expected


@pytest.mark.parametrize(
    "events, expiry",
    [([(0, "spend", 1)], 5), ([(0, "earn", 0)], 5), ([(0, "earn", 1)], 0), ([(3, "earn", 1), (2, "earn", 1)], 5)],
)
def test_invalid(events, expiry):
    with pytest.raises(ValueError):
        loyalty_balance(events, expiry)


def _oracle(events, expiry):
    # One list entry per individual point (its earn day), oldest first.
    pts, out = [], []
    for day, kind, n in events:
        pts = [d for d in pts if d + expiry > day]
        if kind == "earn":
            pts += [day] * n
        elif len(pts) >= n:
            pts = pts[n:]
        out.append(len(pts))
    return out


def test_random_against_oracle():
    rng = random.Random(43)
    for _ in range(200):
        day, events = 0, []
        for _ in range(rng.randint(0, 20)):
            day += rng.choice([0, 0, 1, 2, 5])
            events.append((day, rng.choice(["earn", "redeem"]), rng.randint(1, 8)))
        expiry = rng.randint(1, 8)
        assert list(loyalty_balance(events, expiry)) == _oracle(events, expiry), (events, expiry)
