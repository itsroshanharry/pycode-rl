import re
from fractions import Fraction

# dimension vector order: m, kg, s, A, K, mol, cd
_D = {"m": (1, 0, 0, 0, 0, 0, 0), "kg": (0, 1, 0, 0, 0, 0, 0), "s": (0, 0, 1, 0, 0, 0, 0)}


def _dim(m=0, kg=0, s=0, A=0, K=0, mol=0, cd=0):
    return (m, kg, s, A, K, mol, cd)


_UNITS = {
    "m": (Fraction(1), _dim(m=1)), "g": (Fraction(1, 1000), _dim(kg=1)), "s": (Fraction(1), _dim(s=1)),
    "A": (Fraction(1), _dim(A=1)), "K": (Fraction(1), _dim(K=1)), "mol": (Fraction(1), _dim(mol=1)),
    "cd": (Fraction(1), _dim(cd=1)),
    "N": (Fraction(1), _dim(kg=1, m=1, s=-2)), "Pa": (Fraction(1), _dim(kg=1, m=-1, s=-2)),
    "J": (Fraction(1), _dim(kg=1, m=2, s=-2)), "W": (Fraction(1), _dim(kg=1, m=2, s=-3)),
    "Hz": (Fraction(1), _dim(s=-1)), "bar": (Fraction(100000), _dim(kg=1, m=-1, s=-2)),
    "L": (Fraction(1, 1000), _dim(m=3)), "min": (Fraction(60), _dim(s=1)), "h": (Fraction(3600), _dim(s=1)),
}
_PREFIX = {"G": Fraction(10) ** 9, "M": Fraction(10) ** 6, "k": Fraction(1000), "h": Fraction(100),
           "d": Fraction(1, 10), "c": Fraction(1, 100), "m": Fraction(1, 1000), "u": Fraction(1, 10 ** 6),
           "n": Fraction(1, 10 ** 9)}
_NO_PREFIX = {"min", "h"}
_NUMBER = re.compile(r"-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_FACTOR = re.compile(r"([A-Za-z]+)(?:\^(-?[0-9]+))?")


def _symbol(sym: str) -> tuple[Fraction, Fraction, tuple]:
    """(prefix factor, unit scale, dimension)."""
    if sym in _UNITS:  # a whole unit name wins over prefix + unit
        return (Fraction(1),) + _UNITS[sym]
    if len(sym) > 1 and sym[0] in _PREFIX and sym[1:] in _UNITS and sym[1:] not in _NO_PREFIX:
        return (_PREFIX[sym[0]],) + _UNITS[sym[1:]]
    raise ValueError(f"unknown unit symbol: {sym!r}")


def _units(expr: str) -> tuple[Fraction, tuple]:
    parts = re.split(r"([*/])", expr)
    scale, dim = Fraction(1), (0,) * 7
    for k in range(0, len(parts), 2):
        op = "*" if k == 0 else parts[k - 1]
        token = parts[k]
        if k == 0 and token == "1":
            continue
        m = _FACTOR.fullmatch(token)
        if not m or m.group(2) in ("0", "-0"):
            raise ValueError(f"bad factor: {token!r}")
        p, s, d = _symbol(m.group(1))
        exp = int(m.group(2)) if m.group(2) else 1
        if op == "/":
            exp = -exp  # "/" inverts only this one factor (left-to-right evaluation)
        scale *= (p * s) ** exp  # the exponent applies to the prefixed unit
        dim = tuple(x + exp * y for x, y in zip(dim, d))
    return scale, dim


def _format(x: Fraction) -> str:
    scaled = x * 10 ** 9
    q = scaled.numerator // scaled.denominator
    rest = scaled - q
    if rest > Fraction(1, 2) or (rest == Fraction(1, 2) and q % 2):
        q += 1
    sign = "-" if q < 0 else ""
    q = abs(q)
    whole, frac = divmod(q, 10 ** 9)
    s = f"{whole}.{frac:09d}".rstrip("0").rstrip(".")
    return sign + s if s != "0" else "0"


def convert_quantity(text: str, target: str) -> str:
    number, sep, units = text.partition(" ")
    if sep != " " or not _NUMBER.fullmatch(number) or not units:
        raise ValueError(f"malformed quantity: {text!r}")
    value = Fraction(number)  # exact, also for "2.5e-3"
    s_scale, s_dim = _units(units)
    t_scale, t_dim = _units(target)
    if s_dim != t_dim:
        raise ValueError("dimensions differ")
    return _format(value * s_scale / t_scale)
