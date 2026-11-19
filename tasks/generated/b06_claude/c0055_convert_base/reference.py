import re
from fractions import Fraction

_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
_VALUE = {c: i for i, c in enumerate(_DIGITS)} | {c.upper(): i for i, c in enumerate(_DIGITS) if c.isalpha()}
_NUMBER = re.compile(r"(-?)([0-9A-Za-z]+)(?:\.([0-9A-Za-z]+))?")


def _digit(d: int) -> str:
    return _DIGITS[d]


def convert_base(number: str, from_base: int, to_base: int, frac_digits: int) -> str:
    if not (2 <= from_base <= 36 and 2 <= to_base <= 36) or frac_digits < 0:
        raise ValueError("bad base or frac_digits")
    m = _NUMBER.fullmatch(number)
    if not m:
        raise ValueError(f"malformed number: {number!r}")
    negative, int_s, frac_s = m.group(1) == "-", m.group(2), m.group(3) or ""
    for c in int_s + frac_s:
        if _VALUE[c] >= from_base:
            raise ValueError(f"digit {c!r} not valid in base {from_base}")

    whole = 0
    for c in int_s:
        whole = whole * from_base + _VALUE[c]
    frac_num = 0
    for c in frac_s:
        frac_num = frac_num * from_base + _VALUE[c]
    frac = Fraction(frac_num, from_base ** len(frac_s))  # exact, in [0, 1)

    int_out = ""
    while whole:
        whole, d = divmod(whole, to_base)
        int_out = _digit(d) + int_out
    int_out = int_out or "0"
    frac_out = ""
    for _ in range(frac_digits):
        frac *= to_base
        d = int(frac)  # floor: truncation, not rounding
        frac -= d
        frac_out += _digit(d)

    nonzero = int_out != "0" or any(c != "0" for c in frac_out)
    sign = "-" if negative and nonzero else ""
    return sign + int_out + ("." + frac_out if frac_digits else "")
