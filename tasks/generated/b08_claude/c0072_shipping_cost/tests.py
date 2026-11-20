import random

import pytest
from solution import shipping_cost

R = {"EU": [(1000, 500), (2000, 800), (5000, 1500)], "US": [(500, 900), (10000, 3000)]}
FREE = {"EU": 5000}


@pytest.mark.parametrize(
    "weight, dims, zone, subtotal, expected",
    [
        (1200, (30, 20, 10), "EU", 4999, 800),
        (1200, (30, 20, 10), "EU", 5000, 0),
        (1200, (30, 20, 10), "EU", 999999, 0),
        (1000, (10, 10, 10), "EU", 0, 500),
        (1001, (10, 10, 10), "EU", 0, 800),
        (1, (1, 1, 1), "EU", 0, 500),
        (100, (50, 40, 3), "EU", 0, 800),
        (100, (50, 40, 2), "EU", 0, 500),
        (100, (51, 40, 2), "EU", 0, 500),
        (100, (5000, 1, 1), "EU", 0, 500),
        (100, (5001, 1, 1), "EU", 0, 800),
        (100, (61, 41, 2), "EU", 0, 800),
        (100, (10, 10, 1), "US", 0, 900),
        (501, (10, 10, 1), "US", 0, 3000),
        (4999, (1, 1, 1), "EU", 0, 1500),
        (5000, (1, 1, 1), "EU", 0, 1500),
        (100, (100, 50, 5), "EU", 0, 1500),
        (100, (10, 10, 1), "US", 10 ** 9, 900),
        (2000, (100, 10, 10), "EU", 0, 800),
        (2000, (100, 10, 11), "EU", 0, 1500),
    ],
)
def test_examples(weight, dims, zone, subtotal, expected):
    assert shipping_cost(weight, dims, zone, subtotal, R, FREE) == expected


@pytest.mark.parametrize(
    "weight, dims, zone",
    [(0, (1, 1, 1), "EU"), (1, (0, 1, 1), "EU"), (1, (1, 1, -2), "EU"), (1, (1, 1, 1), "XX"), (5001, (1, 1, 1), "EU"),
     (100, (100, 50, 6), "EU"), (10001, (1, 1, 1), "US")],
)
def test_invalid(weight, dims, zone):
    with pytest.raises(ValueError):
        shipping_cost(weight, dims, zone, 0, R, FREE)


@pytest.mark.parametrize("weight, expected", [(600, 2), (999, 2), (1000, 2), (400, 1), (500, 1), (1001, 3)])
def test_brackets_not_on_500g_steps(weight, expected):
    # billable weight is rounded up to 500 g BEFORE the bracket lookup: 600 g bills as 1000 g > 999
    rates = {"X": [(999, 1), (1499, 2), (1500, 3)]}
    assert shipping_cost(weight, (1, 1, 1), "X", 0, rates, {}) == expected


def test_too_heavy_even_when_free():
    with pytest.raises(ValueError):
        shipping_cost(6000, (1, 1, 1), "EU", 10 ** 6, R, FREE)


def _oracle(w, dims, zone, sub):
    vol = dims[0] * dims[1] * dims[2]
    dim_w = vol // 5 + (1 if vol % 5 else 0)
    bill = max(w, dim_w)
    if bill % 500:
        bill += 500 - bill % 500
    price = next((p for m, p in R[zone] if bill <= m), None)
    if price is None:
        return "error"
    return 0 if zone in FREE and sub >= FREE[zone] else price


def test_random_against_oracle():
    rng = random.Random(42)
    for _ in range(500):
        w = rng.randint(1, 6000)
        dims = tuple(rng.randint(1, 60) for _ in range(3))
        zone = rng.choice(["EU", "US"])
        sub = rng.choice([0, 4999, 5000, 5001])
        want = _oracle(w, dims, zone, sub)
        if want == "error":
            with pytest.raises(ValueError):
                shipping_cost(w, dims, zone, sub, R, FREE)
        else:
            assert shipping_cost(w, dims, zone, sub, R, FREE) == want, (w, dims, zone, sub)
