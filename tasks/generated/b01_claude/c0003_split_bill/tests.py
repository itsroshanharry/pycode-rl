import math
import random
from fractions import Fraction

import pytest
from solution import split_bill


@pytest.mark.parametrize(
    "total, weights, expected",
    [
        (1000, {"ann": 1, "bob": 1, "cy": 1}, {"ann": 334, "bob": 333, "cy": 333}),
        (100, {"a": 2, "b": 1}, {"a": 67, "b": 33}),
        (0, {"a": 1, "b": 2}, {"a": 0, "b": 0}),
        (1, {"b": 1, "a": 1}, {"a": 1, "b": 0}),
        (7, {"x": 5}, {"x": 7}),
        (10, {"a": 1, "b": 1, "c": 1, "d": 1}, {"a": 3, "b": 3, "c": 2, "d": 2}),
        (100, {"a": 1, "b": 2, "c": 3}, {"a": 17, "b": 33, "c": 50}),
        (5, {"z": 3, "y": 3, "x": 1}, {"z": 2, "y": 2, "x": 1}),
        (99999999999, {"a": 3, "b": 7}, {"a": 30000000000, "b": 69999999999}),
        (1, {"b": 1, "B": 1}, {"B": 1, "b": 0}),
    ],
)
def test_examples(total, weights, expected):
    assert dict(split_bill(total, weights)) == expected


@pytest.mark.parametrize("weights", [{}, {"a": 0}, {"a": 2, "b": -1}, {"a": 1.5}, {"a": "2"}])
def test_invalid(weights):
    with pytest.raises(ValueError):
        split_bill(100, weights)


def _oracle(total, weights):
    # Exact fractions: floor of the ideal share, then leftovers by fractional part.
    w_sum = sum(weights.values())
    ideal = {n: Fraction(total * w, w_sum) for n, w in weights.items()}
    out = {n: math.floor(v) for n, v in ideal.items()}
    leftover = total - sum(out.values())
    for n in sorted(weights, key=lambda n: (-(ideal[n] - out[n]), n))[:leftover]:
        out[n] += 1
    return out


def test_random_against_oracle():
    rng = random.Random(40)
    names = ["al", "Bo", "cy", "di", "ed", "Al", "fay"]
    for _ in range(200):
        people = rng.sample(names, rng.randint(1, len(names)))
        weights = {p: rng.randint(1, 9) for p in people}
        total = rng.choice([0, 1, 2, rng.randint(0, 50), rng.randint(0, 10**6)])
        result = dict(split_bill(total, weights))
        assert result == _oracle(total, weights), (total, weights)
        assert sum(result.values()) == total
