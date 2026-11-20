import re
from fractions import Fraction

_P = re.compile(r"(100|[0-9]{1,2})(?:\.[0-9]+)?")


def _format6(x: Fraction) -> str:
    scaled = x * 10 ** 6
    q = scaled.numerator // scaled.denominator
    rest = scaled - q
    if rest > Fraction(1, 2) or (rest == Fraction(1, 2) and q % 2):
        q += 1
    sign = "-" if q < 0 else ""
    q = abs(q)
    return f"{sign}{q // 10 ** 6}.{q % 10 ** 6:06d}"


def percentile(values: list[int], p: str, method: str) -> str:
    if not values or method not in ("linear", "lower", "higher", "nearest", "midpoint"):
        raise ValueError("empty values or unknown method")
    if not _P.fullmatch(p) or Fraction(p) > 100:
        raise ValueError(f"bad percentile: {p!r}")
    xs = sorted(values)
    h = Fraction(len(xs) - 1) * Fraction(p) / 100
    lo = h.numerator // h.denominator
    hi = lo if h == lo else lo + 1
    if method == "linear":
        result = xs[lo] + (h - lo) * (xs[hi] - xs[lo])
    elif method == "lower":
        result = Fraction(xs[lo])
    elif method == "higher":
        result = Fraction(xs[hi])
    elif method == "nearest":
        frac = h - lo
        idx = hi if frac > Fraction(1, 2) or (frac == Fraction(1, 2) and lo % 2) else lo  # .5 -> even index
        result = Fraction(xs[idx])
    else:
        result = Fraction(xs[lo] + xs[hi], 2)
    return _format6(result)
