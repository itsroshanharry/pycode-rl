```python
def fiscal_label(date: str, start_month: int) -> str:
    """Fiscal year and quarter label such as "FY2025-Q3".

    The fiscal year starts on day 1 of `start_month` (1..12) and is named after the
    calendar year in which it ENDS: with start_month = 4, April 2024 through March
    2025 is FY2025. With start_month = 1 the fiscal year is the calendar year.
    Quarters are consecutive 3-month blocks starting at start_month (Q1 is the first
    three months of the fiscal year). `date` is in the exact form "YYYY-MM-DD".
    Raise ValueError for a malformed or invalid date, or a start_month that is not an
    int in 1..12.

    >>> fiscal_label("2024-05-10", 4)
    'FY2025-Q1'
    >>> fiscal_label("2024-03-31", 4)
    'FY2024-Q4'
    """
```
