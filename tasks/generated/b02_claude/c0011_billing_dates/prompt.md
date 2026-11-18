```python
def billing_dates(anchor: str, count: int) -> list[str]:
    """Return the first `count` monthly billing dates of a subscription.

    `anchor` is the first billing date in the exact form "YYYY-MM-DD". Billing date
    number k (k = 0, 1, 2, ...) falls k calendar months after the anchor, on the
    anchor's day of the month; if that month is too short, use its last day. The
    day always comes from the anchor, never from the previous billing date (so an
    anchor of Jan 31 gives Feb 29 in a leap year and then Mar 31).
    Raise ValueError if `anchor` is not a valid date in that exact form or if
    count is negative. count == 0 gives [].

    >>> billing_dates("2024-01-31", 4)
    ['2024-01-31', '2024-02-29', '2024-03-31', '2024-04-30']
    >>> billing_dates("2023-11-15", 3)
    ['2023-11-15', '2023-12-15', '2024-01-15']
    """
```
