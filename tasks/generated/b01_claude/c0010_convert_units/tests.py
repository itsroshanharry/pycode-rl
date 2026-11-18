import random
from fractions import Fraction

import pytest
from solution import convert_units

LENGTH = [("ft", "in", "12"), ("in", "cm", "2.54")]
TIME = [("h", "min", "60"), ("min", "s", "60")]


@pytest.mark.parametrize(
    "amount, src, dst, factors, expected",
    [
        ("1", "ft", "cm", LENGTH, "762/25"),
        ("100", "cm", "ft", LENGTH, "1250/381"),
        ("3/4", "a", "a", [], "3/4"),
        ("-1.5", "m", "m", [], "-3/2"),
        ("2", "h", "s", TIME, "7200"),
        ("7200", "s", "h", TIME, "2"),
        ("1", "s", "h", TIME, "1/3600"),
        ("0", "ft", "cm", LENGTH, "0"),
        ("-0", "a", "a", [], "0"),
        ("10", "x", "z", [("y", "x", "1/2"), ("y", "z", "3")], "60"),
        ("1", "kg", "g", [("kg", "g", "1000.000")], "1000"),
        ("0.1", "a", "b", [("a", "b", "3")], "3/10"),
        ("1", "u0", "u20", [(f"u{i}", f"u{i + 1}", "2") for i in range(20)], "1048576"),
        ("1/3", "a", "b", [("a", "b", "1/3")], "1/9"),
        ("-2.5", "in", "ft", LENGTH, "-5/24"),
        ("1", "cm", "cm", LENGTH, "1"),
    ],
)
def test_examples(amount, src, dst, factors, expected):
    assert convert_units(amount, src, dst, factors) == expected


@pytest.mark.parametrize(
    "amount, src, dst, factors",
    [
        ("1", "a", "d", [("a", "b", "2"), ("c", "d", "5")]),
        ("1", "a", "q", [("a", "b", "2")]),
        ("1e3", "a", "a", []), (".5", "a", "a", []), ("1.", "a", "a", []), ("1/0", "a", "a", []),
        ("abc", "a", "a", []), ("--1", "a", "a", []), (" 1", "a", "a", []), ("+1", "a", "a", []),
        ("1", "a", "b", [("a", "b", "-2")]), ("1", "a", "b", [("a", "b", "0")]),
        ("1", "a", "b", [("a", "b", "0/5")]), ("1", "a", "b", [("a", "b", "1/0")]),
        ("1", "a", "b", [("a", "b", "2."), ]), ("1", "a", "a", [("x", "y", "+3")]),
    ],
)
def test_invalid(amount, src, dst, factors):
    with pytest.raises(ValueError):
        convert_units(amount, src, dst, factors)


def _fmt(fr):
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def test_random_against_absolute_values():
    # Give every unit an absolute size; derive consistent factors from it; then
    # conversion is just amount * size(src) / size(dst).
    rng = random.Random(71)
    for _ in range(150):
        n = rng.randint(1, 8)
        size = {f"u{i}": Fraction(rng.randint(1, 50), rng.randint(1, 50)) for i in range(n)}
        names = list(size)
        factors = []
        for i in range(1, n):  # random spanning tree, edges in random directions
            a, b = names[i], names[rng.randrange(i)]
            if rng.random() < 0.5:
                a, b = b, a
            f = size[a] / size[b]
            factors.append((a, b, f"{f.numerator}/{f.denominator}"))
        rng.shuffle(factors)
        src, dst = rng.choice(names), rng.choice(names)
        amt = Fraction(rng.randint(-99, 99), rng.randint(1, 20))
        amount = f"{amt.numerator}/{amt.denominator}" if amt >= 0 else f"-{-amt.numerator}/{amt.denominator}"
        assert convert_units(amount, src, dst, factors) == _fmt(amt * size[src] / size[dst]), (amount, src, dst, factors)
