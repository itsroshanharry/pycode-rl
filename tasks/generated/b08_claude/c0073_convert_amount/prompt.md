```python
def convert_amount(amount: str, src: str, dst: str, rates: list[tuple[str, str, str]]) -> str:
    """Convert money between currencies through a chain of exchange rates.

    Each rate (A, B, r) means 1 A = r B, where r is a positive decimal string
    (ASCII digits with an optional "." part, e.g. "1.0842", "150"). A rate can
    also be used backwards: 1 B = 1/r A. There is at most one rate per pair of
    currencies in either direction (ValueError otherwise, including a rate
    from a currency to itself).

    Choose the conversion path with the FEWEST conversions; if several
    shortest paths exist, use the one whose list of currency codes is
    smallest in plain string (lexicographic) order, comparing code by code.
    Multiply exactly along the path (no floats), then round to 2 decimal
    places with ties to even (banker's rounding). If src == dst no rate is
    used. Return the result as a string with exactly 2 decimals and a
    leading "-" only if the rounded result is negative ("-0.00" is "0.00").

    `amount` is an optional "-", ASCII digits, and an optional "." part.
    Raise ValueError for a malformed amount or rate, or if dst cannot be
    reached from src.

    >>> convert_amount("100", "EUR", "JPY", [("EUR", "USD", "1.08"), ("USD", "JPY", "150")])
    '16200.00'
    >>> convert_amount("162", "JPY", "EUR", [("EUR", "USD", "1.08"), ("USD", "JPY", "150")])
    '1.00'
    """
```
