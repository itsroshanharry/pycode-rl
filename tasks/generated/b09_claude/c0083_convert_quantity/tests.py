import re
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from fractions import Fraction

import pytest
from solution import convert_quantity

# ---- independent oracle: full symbol table built up front, Decimal formatting ----
BASE = {  # symbol -> (scale, {dimension: exponent})
    "m": (1, {"m": 1}), "g": (Fraction(1, 1000), {"kg": 1}), "s": (1, {"s": 1}), "A": (1, {"A": 1}),
    "K": (1, {"K": 1}), "mol": (1, {"mol": 1}), "cd": (1, {"cd": 1}),
    "N": (1, {"kg": 1, "m": 1, "s": -2}), "Pa": (1, {"kg": 1, "m": -1, "s": -2}), "J": (1, {"kg": 1, "m": 2, "s": -2}),
    "W": (1, {"kg": 1, "m": 2, "s": -3}), "Hz": (1, {"s": -1}), "bar": (100000, {"kg": 1, "m": -1, "s": -2}),
    "L": (Fraction(1, 1000), {"m": 3}), "min": (60, {"s": 1}), "h": (3600, {"s": 1}),
}
PREF = {"G": 10 ** 9, "M": 10 ** 6, "k": 1000, "h": 100, "d": Fraction(1, 10), "c": Fraction(1, 100),
        "m": Fraction(1, 1000), "u": Fraction(1, 10 ** 6), "n": Fraction(1, 10 ** 9)}
TABLE = dict(BASE)
for p, f in PREF.items():
    for u, (sc, dim) in BASE.items():
        if u not in ("min", "h") and p + u not in BASE:
            TABLE.setdefault(p + u, (f * Fraction(sc), dim))


def _parse_units(expr):
    tokens = re.findall(r"[*/]|[^*/]+", expr)
    if not tokens or tokens[0] in "*/" or tokens[-1] in "*/" or any(a in "*/" and b in "*/" for a, b in zip(tokens, tokens[1:])):
        raise ValueError
    scale, dims, sign = Fraction(1), {}, 1
    for i, tok in enumerate(tokens):
        if tok in "*/":
            sign = 1 if tok == "*" else -1
            continue
        if i == 0 and tok == "1":
            continue
        name, _, power = tok.partition("^")
        if name not in TABLE or (_ and not re.fullmatch(r"-?[1-9][0-9]*", power)):
            raise ValueError
        e = sign * (int(power) if _ else 1)
        sc, dim = TABLE[name]
        scale *= Fraction(sc) ** e
        for k, v in dim.items():
            dims[k] = dims.get(k, 0) + e * v
        sign = 1
    return scale, {k: v for k, v in dims.items() if v}


def _oracle(text, target):
    num, units = text.split(" ")
    s1, d1 = _parse_units(units)
    s2, d2 = _parse_units(target)
    assert d1 == d2
    x = Fraction(num) * s1 / s2
    with localcontext() as ctx:
        ctx.prec = 200
        d = (Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal("1e-9"), rounding=ROUND_HALF_EVEN)
    s = format(d, "f").rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


VALID = [
    ("1 km/h", "m/s"), ("3 kg*m/s^2", "N"), ("1 h", "min"), ("1 hPa", "Pa"), ("1 h*Pa", "Pa*s"),
    ("1 cm^2", "m^2"), ("1 m^2", "cm^2"), ("1 m/s*kg", "kg*m/s"), ("2 m/s/kg", "m/kg/s"), ("1 m/s*s", "m"),
    ("1 L", "m^3"), ("1 mL", "cm^3"), ("1 bar", "kPa"), ("1 mbar", "hPa"), ("1 kW*h", "J"), ("60 1/min", "Hz"),
    ("2.5e-3 km", "m"), ("1e3 m", "km"), ("-0.0000000004 m", "m"), ("0.0000000005 m", "m"), ("0.0000000015 m", "m"),
    ("0.0000000025 m", "m"), ("1.0000000005 m", "m"), ("123456789.123456789123 mm", "km"), ("1 cd", "cd"),
    ("1 mol/L", "mol/m^3"), ("1 g", "kg"), ("1 Mg", "kg"), ("1 us", "ns"), ("1 min", "s"), ("1 MHz", "1/s"),
    ("1 N*m", "J"), ("1 W", "J/s"), ("7 km^-1", "1/m"), ("1 dm^3", "L"), ("3 GPa", "N/mm^2"), ("-12.5 kN*m/s^2", "N*m/s^2"),
    ("1 m*m*m", "L"), ("5 A*s", "mA*h"), ("1 K/s", "K/min"), ("1 nm/us", "mm/s"),
]

# Literal values below were produced by _oracle (not by hand).
FIXED = {("1 km/h", "m/s"): "0.277777778", ("3 kg*m/s^2", "N"): "3", ("1 cm^2", "m^2"): "0.0001",
         ("1 m/s*s", "m"): "1", ("0.0000000005 m", "m"): "0", ("0.0000000015 m", "m"): "0.000000002",
         ("0.0000000025 m", "m"): "0.000000002", ("-0.0000000004 m", "m"): "0", ("1 h*Pa", "Pa*s"): "3600",
         ("1 kW*h", "J"): "3600000", ("5 A*s", "mA*h"): "1.388888889"}


@pytest.mark.parametrize("text, target", VALID)
def test_against_oracle(text, target):
    got = convert_quantity(text, target)
    assert got == _oracle(text, target)
    if (text, target) in FIXED:
        assert got == FIXED[(text, target)]


@pytest.mark.parametrize(
    "text, target",
    [
        ("1km", "m"), ("1  km", "m"), ("km", "m"), ("1 km/", "m"), ("1 /km", "1/m"), ("1 k", "m"), ("1 kmin", "s"),
        ("1 mmin", "s"), ("1 km^0", "m"), ("1 km^", "m"), ("1 km^1.5", "m"), ("1 Km", "m"), ("1 m", "s"), ("+1 m", "m"),
        ("1. m", "m"), (".5 m", "m"), ("1 m*1", "m"), ("1 m**s", "m*s"), ("1 kh", "s"), ("1 N", "kg*m/s"), ("1 m", "m^2"),
        ("1 m", "foo"), ("1 m ", "m"), (" 1 m", "m"), ("1e m", "m"), ("１ m", "m"), ("1 m", ""), ("1 m", "m/"),
    ],
)
def test_invalid(text, target):
    with pytest.raises(ValueError):
        convert_quantity(text, target)
