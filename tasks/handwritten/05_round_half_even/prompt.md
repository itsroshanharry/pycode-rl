```python
def round_half_even(number: str, places: int) -> str:
    """Round a decimal number given as a string, using round-half-to-even.

    `number` is an optional minus sign, one or more digits, and optionally a
    decimal point followed by one or more digits; `places` >= 0. Round it
    to `places` digits after the decimal point. A value exactly halfway between
    the two nearest candidates goes to the one whose last kept digit is even. The
    rounding must be exact on the decimal digits (no binary floating-point error).
    Return the result with exactly `places` digits after the point (and no point
    when places == 0), without leading zeros except a single "0" before the point,
    and without a minus sign when the rounded result is zero.

    >>> round_half_even("2.675", 2)
    '2.68'
    >>> round_half_even("1.25", 1)
    '1.2'
    >>> round_half_even("-0.5", 0)
    '0'
    """
```
