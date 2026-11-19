import random
from fractions import Fraction

import pytest
from solution import apply_discounts


def P(code, v, g=None):
    return {"code": code, "kind": "percent", "value": v, "group": g}


def F(code, v, g=None):
    d = {"code": code, "kind": "fixed", "value": v}
    if g is not None:
        d["group"] = g
    return d


@pytest.mark.parametrize(
    "subtotal, coupons, expected",
    [
        (10000, [F("F5", 500), P("P10", 10)], (8500, ["P10", "F5"])),
        (10000, [P("P10", 10), F("F5", 500)], (8500, ["P10", "F5"])),
        (10000, [], (10000, [])),
        (0, [P("P10", 10), F("F1", 1)], (0, ["P10", "F1"])),
        (10000, [P("P10", 10), P("P20", 20)], (7200, ["P10", "P20"])),
        (1005, [P("P10", 10)], (904, ["P10"])),
        (999, [P("P15", 15)], (849, ["P15"])),
        (995, [P("P10", 10)], (895, ["P10"])),
        (10000, [P("P10", 10, "A"), F("F15", 1500, "A")], (8500, ["F15"])),
        (10000, [P("P10", 10, "A"), F("F10", 1000, "A")], (9000, ["P10"])),
        (10000, [F("F10", 1000, "A"), P("P10", 10, "A")], (9000, ["F10"])),
        (3000, [F("F50", 5000, "A"), F("F90", 9000, "A")], (0, ["F50"])),
        (3000, [F("F50", 5000, "A"), P("P100", 100, "A")], (0, ["F50"])),
        (3000, [F("F20", 2000, "A"), F("F90", 9000, "A")], (0, ["F90"])),
        (1000, [F("A", 600), F("B", 600)], (0, ["A", "B"])),
        (1000, [P("ALL", 100), F("X", 5)], (0, ["ALL", "X"])),
        (10000, [P("a", 10, "g1"), P("b", 20, "g1"), P("c", 5, "g2"), F("d", 100), P("e", 50, "g2")],
         (3900, ["b", "e", "d"])),
        (10000, [P("x", 10, None), P("y", 10, None)], (8100, ["x", "y"])),
        (2000, [P("p", 30, "g"), F("f", 600, "g"), F("h", 601, "g")], (1399, ["h"])),
    ],
)
def test_examples(subtotal, coupons, expected):
    total, codes = apply_discounts(subtotal, coupons)
    assert (total, list(codes)) == expected


@pytest.mark.parametrize(
    "subtotal, coupons",
    [
        (-1, []),
        (100, [{"code": "b", "kind": "bogo", "value": 1}]),
        (100, [P("p", 0)]),
        (100, [P("p", 101)]),
        (100, [F("f", 0)]),
        (100, [F("f", -5)]),
        (100, [P("x", 10), F("x", 5)]),
    ],
)
def test_invalid(subtotal, coupons):
    with pytest.raises(ValueError):
        apply_discounts(subtotal, coupons)


def _oracle(subtotal, coupons):
    def nominal(c):
        return Fraction(subtotal * c["value"], 100) if c["kind"] == "percent" else Fraction(min(c["value"], subtotal))

    keep = []
    for i, c in enumerate(coupons):
        g = c.get("group")
        if g is None:
            keep.append(c)
            continue
        rivals = [(nominal(d), -j) for j, d in enumerate(coupons) if d.get("group") == g]
        if max(rivals) == (nominal(c), -i):
            keep.append(c)
    total, codes = Fraction(subtotal), []
    for c in keep:
        if c["kind"] == "percent":
            disc = total * c["value"] / 100
            total -= int(disc + Fraction(1, 2))
            codes.append(c["code"])
    for c in keep:
        if c["kind"] == "fixed":
            total = max(Fraction(0), total - c["value"])
            codes.append(c["code"])
    return int(total), codes


def test_random_against_oracle():
    rng = random.Random(44)
    for _ in range(400):
        coupons = []
        for k in range(rng.randint(0, 6)):
            g = rng.choice([None, "A", "B"])
            if rng.random() < 0.5:
                coupons.append(P(f"c{k}", rng.choice([1, 5, 10, 15, 33, 50, 100]), g))
            else:
                coupons.append(F(f"c{k}", rng.choice([1, 99, 500, 1000, 2500, 99999]), g))
        subtotal = rng.choice([0, 1, 99, 995, 1005, 2000, 10000, 12345])
        total, codes = apply_discounts(subtotal, coupons)
        assert (total, list(codes)) == _oracle(subtotal, coupons), (subtotal, coupons)
