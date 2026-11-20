import itertools
import random
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction

import pytest
from solution import convert_amount

BASIC = [("EUR", "USD", "1.08"), ("USD", "JPY", "150")]


@pytest.mark.parametrize(
    "amount, src, dst, rates, expected",
    [
        ("100", "EUR", "JPY", BASIC, "16200.00"),
        ("162", "JPY", "EUR", BASIC, "1.00"),
        ("1", "USD", "EUR", BASIC, "0.93"),
        ("12.345", "EUR", "EUR", [], "12.34"),
        ("12.355", "EUR", "EUR", [], "12.36"),
        ("-12.345", "EUR", "EUR", [], "-12.34"),
        ("-0.004", "EUR", "EUR", [], "0.00"),
        ("-0.005", "EUR", "EUR", [], "0.00"),
        ("-0.015", "EUR", "EUR", [], "-0.02"),
        ("0", "EUR", "JPY", BASIC, "0.00"),
        ("1", "A", "B", [("A", "B", "0.125")], "0.12"),
        ("1", "A", "B", [("A", "B", "0.135")], "0.14"),
        ("3", "B", "A", [("A", "B", "3")], "1.00"),
        ("1", "B", "A", [("A", "B", "3")], "0.33"),
        ("2", "B", "A", [("A", "B", "3")], "0.67"),
        # inconsistent rates: the direct (1-hop) path wins over a 2-hop path
        ("100", "A", "C", [("A", "B", "2"), ("B", "C", "2"), ("A", "C", "3")], "300.00"),
        # two 2-hop paths A-B-D and A-C-D: lexicographically smaller (via B) wins
        ("100", "A", "D", [("A", "C", "1"), ("C", "D", "5"), ("A", "B", "1"), ("B", "D", "2")], "200.00"),
        ("100", "D", "A", [("A", "C", "1"), ("C", "D", "5"), ("A", "B", "1"), ("B", "D", "2")], "50.00"),
        # comparison is code by code: path [A, AB, Z] < [A, B, Z]
        ("1", "A", "Z", [("A", "B", "1"), ("B", "Z", "7"), ("A", "AB", "1"), ("AB", "Z", "9")], "9.00"),
        ("10", "X", "Y", [("Y", "X", "4")], "2.50"),
        ("1", "GBP", "JPY", [("GBP", "EUR", "1.17"), ("EUR", "USD", "1.08"), ("USD", "JPY", "151.25")], "191.12"),
    ],
)
def test_examples(amount, src, dst, rates, expected):
    assert convert_amount(amount, src, dst, rates) == expected


@pytest.mark.parametrize(
    "amount, src, dst, rates",
    [
        ("1", "A", "C", [("A", "B", "2")]),
        ("1", "A", "B", [("A", "B", "0")]),
        ("1", "A", "B", [("A", "B", "-1")]),
        ("1", "A", "B", [("A", "B", "1e3")]),
        ("1", "A", "B", [("A", "B", ".5")]),
        ("1", "A", "B", [("A", "B", "2"), ("A", "B", "2")]),
        ("1", "A", "B", [("A", "B", "2"), ("B", "A", "0.5")]),
        ("1", "A", "B", [("A", "A", "1"), ("A", "B", "2")]),
        ("1.", "A", "A", []),
        ("+1", "A", "A", []),
        ("1,5", "A", "A", []),
        ("", "A", "A", []),
        ("１", "A", "A", []),
    ],
)
def test_invalid(amount, src, dst, rates):
    with pytest.raises(ValueError):
        convert_amount(amount, src, dst, rates)


def _oracle(amount, src, dst, rates):
    g = {}
    for a, b, r in rates:
        g.setdefault(a, {})[b] = Fraction(r)
        g.setdefault(b, {})[a] = 1 / Fraction(r)
    nodes = sorted(g)
    best = None
    if src == dst:
        best = [src]
    else:
        for k in range(0, len(nodes)):
            for mid in itertools.permutations([n for n in nodes if n not in (src, dst)], k):
                path = [src, *mid, dst]
                if all(y in g.get(x, {}) for x, y in zip(path, path[1:])):
                    if best is None or path < best:
                        best = path
            if best is not None:
                break
    v = Fraction(amount)
    for x, y in zip(best, best[1:]):
        v *= g[x][y]
    with localcontext() as ctx:
        ctx.prec = 100
        d = (Decimal(v.numerator) / Decimal(v.denominator)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    s = f"{d:.2f}"
    return "0.00" if s == "-0.00" else s


def test_random_against_oracle():
    rng = random.Random(45)
    codes = ["AUD", "CHF", "EUR", "GBP", "JPY", "USD"]
    for _ in range(150):
        pairs = rng.sample(list(itertools.combinations(codes, 2)), rng.randint(2, 7))
        rates = []
        for a, b in pairs:
            if rng.random() < 0.5:
                a, b = b, a
            rates.append((a, b, rng.choice(["0.5", "1.25", "2", "3", "0.8", "151.3", "1.0842"])))
        reach = {x for r in rates for x in r[:2]}
        src, dst = rng.choice(sorted(reach)), rng.choice(sorted(reach))
        amount = rng.choice(["1", "100", "-37.5", "0.01", "12345.678"])
        try:
            want = _oracle(amount, src, dst, rates)
        except TypeError:  # no path (best is None)
            with pytest.raises(ValueError):
                convert_amount(amount, src, dst, rates)
            continue
        assert convert_amount(amount, src, dst, rates) == want, (amount, src, dst, rates)
