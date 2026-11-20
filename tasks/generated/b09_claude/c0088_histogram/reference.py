import re
from fractions import Fraction

_NUM = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")


def _exact(s: str) -> Fraction:
    if not _NUM.fullmatch(s):
        raise ValueError(f"bad number: {s!r}")
    return Fraction(s)  # exact decimal value; float("0.3") / 0.1 would be 2.9999999999999996


def histogram(values: list[str], lo: str, hi: str, width: str) -> tuple[list[int], int, int]:
    a, b, w = _exact(lo), _exact(hi), _exact(width)
    if a >= b or w <= 0:
        raise ValueError("need lo < hi and width > 0")
    span = (b - a) / w
    n = -((-span.numerator) // span.denominator)  # ceil
    counts = [0] * n
    under = over = 0
    for s in values:
        x = _exact(s)
        if x < a:
            under += 1
        elif x > b:
            over += 1
        else:
            i = (x - a) // w  # floor of an exact Fraction
            counts[min(int(i), n - 1)] += 1  # x == hi falls into the last bin
    return counts, under, over
