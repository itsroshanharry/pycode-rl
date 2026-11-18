from math import gcd


def mixed_number(numerator: int, denominator: int) -> str:
    if denominator == 0:
        raise ZeroDivisionError("denominator is zero")
    negative = (numerator < 0) != (denominator < 0) and numerator != 0
    sign = "-" if negative else ""
    n, d = abs(numerator), abs(denominator)
    g = gcd(n, d)
    n, d = n // g, d // g
    whole, rest = divmod(n, d)
    if rest == 0:
        return f"{sign}{whole}"
    if whole == 0:
        return f"{sign}{rest}/{d}"
    return f"{sign}{whole} {rest}/{d}"
