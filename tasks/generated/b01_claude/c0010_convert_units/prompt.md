```python
def convert_units(amount: str, from_unit: str, to_unit: str, factors: list[tuple[str, str, str]]) -> str:
    """Convert an exact quantity between units using a table of conversion factors.

    Each factor (a, b, f) means 1 a = f b. Factors can be used in both directions
    (1 b = 1/f a) and chained through any number of other units. If several chains
    exist, you may assume they give the same result. Converting a unit to itself
    always works, even if the unit appears in no factor.
    Number strings are either digits with an optional "." and more digits
    ("12", "2.54") or digits "/" digits with a non-zero denominator ("1/3"). The
    amount may also start with "-"; a factor may not and must not be zero. No
    spaces, exponents or other forms are allowed.
    Return the exact result as a reduced fraction "p/q" (q > 1), or as an integer
    string "p" when it is whole (zero is "0", never "-0").
    Raise ValueError for a malformed number, a zero or negative factor (every factor
    is checked, even unused ones), or when no chain connects the two units.

    >>> convert_units("1", "ft", "cm", [("ft", "in", "12"), ("in", "cm", "2.54")])
    '762/25'
    >>> convert_units("100", "cm", "ft", [("ft", "in", "12"), ("in", "cm", "2.54")])
    '1250/381'
    """
```
