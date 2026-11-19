```python
def format_number(value: str, decimal_mark: str, group_sep: str, grouping: list[int], frac_digits: int) -> str:
    """Format a decimal number with explicitly given locale rules.

    `value` is a decimal string: an optional "-", one or more ASCII digits,
    and optionally "." followed by one or more ASCII digits (no "+", no
    exponent, no spaces). It may have any number of digits.

    1. Round the exact value to `frac_digits` decimal places, with ties
       rounded to the even last digit (banker's rounding).
    2. Group the digits of the integer part from the right: the first group
       has grouping[0] digits, the next grouping[1], and so on; the LAST size
       repeats for all further groups (so [3, 2] gives "12,34,56,789").
       An empty `grouping` means no grouping. Groups are joined by `group_sep`.
    3. If frac_digits > 0, append `decimal_mark` and exactly `frac_digits`
       digits. Leading zeros of the integer part are dropped (but keep one "0").
    4. Prefix "-" only if the ROUNDED value is not zero.

    Raise ValueError for a malformed `value`, frac_digits < 0, a grouping size
    < 1, an empty mark/separator, or decimal_mark == group_sep.

    >>> format_number("1234567.891", ",", ".", [3], 2)
    '1.234.567,89'
    >>> format_number("123456789", ".", ",", [3, 2], 0)
    '12,34,56,789'
    """
```
