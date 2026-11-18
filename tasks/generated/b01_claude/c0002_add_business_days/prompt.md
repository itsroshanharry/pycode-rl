```python
def add_business_days(start: str, n: int, holidays: list[str]) -> str:
    """Move `n` business days from `start` and return the resulting date.

    Dates are strings in the exact form "YYYY-MM-DD" (4-digit year, 2-digit month
    and day). A business day is a Monday to Friday that is not listed in
    `holidays`; holidays may contain duplicates or weekend dates.
    For n > 0, step forward one calendar day at a time, counting business days,
    and return the day on which the count reaches n. For n < 0, do the same
    backwards with abs(n). For n == 0, return `start` if it is a business day,
    otherwise the first business day after it. abs(n) <= 10_000.
    Raise ValueError if `start` or any holiday is not a valid date in that exact
    form (for example "2024-3-8", "20240308" or "2024-02-30").

    >>> add_business_days("2024-03-08", 1, [])      # a Friday -> next Monday
    '2024-03-11'
    >>> add_business_days("2024-12-24", 2, ["2024-12-25", "2024-12-26"])
    '2024-12-30'
    """
```
