```python
def convert_base(number: str, from_base: int, to_base: int, frac_digits: int) -> str:
    """Convert a number written in base `from_base` to base `to_base` (2..36).

    `number` is an optional "-", one or more digits, and optionally "." plus
    one or more digits. Digits are 0-9 then a-z for 10-35 (uppercase A-Z is
    accepted as input); every digit must be less than `from_base`. Nothing
    else is allowed (no "+", spaces, underscores, prefixes like "0x", or
    non-ASCII characters).

    Output: the integer part in `to_base` with no leading zeros ("0" if it is
    zero), then, if frac_digits > 0, "." and EXACTLY `frac_digits` fractional
    digits. Fractional digits are TRUNCATED (cut toward zero), never rounded.
    Digits above 9 are lowercase. The result has a leading "-" only if the
    number is negative and at least one output digit is non-zero.
    The conversion must be exact (no floating point).

    Raise ValueError for a malformed number, a digit not valid in
    `from_base`, a base outside 2..36, or frac_digits < 0.

    >>> convert_base("-1a.8", 16, 2, 4)
    '-11010.1000'
    >>> convert_base("0.1", 10, 2, 8)
    '0.00011001'
    """
```
