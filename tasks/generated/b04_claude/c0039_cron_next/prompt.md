```python
def cron_next(expr: str, after: str) -> str | None:
    """Return the first minute strictly after `after` that matches a cron expression.

    `expr` has exactly 5 whitespace-separated fields (extra whitespace anywhere
    around them is ignored): minute (0-59), hour (0-23), day-of-month (1-31),
    month (1-12), day-of-week (0-6, 0 = Sunday; 7 is NOT accepted).
    Each field is a comma-separated list of items, and each item is one of
      "*"      every value of the field
      "N"      a single value
      "N-M"    the values N..M inclusive (N <= M)
    optionally followed by "/S" (S >= 1), which keeps every S-th value counting
    from the start of the item: "*/S" starts at the field's minimum, "N-M/S" at
    N, and "N/S" means N through the field's maximum in steps of S.
    Numbers are ASCII digits (leading zeros allowed); names like JAN or MON are
    not supported.

    Day rule: a field is "restricted" unless it is exactly "*". If BOTH
    day-of-month and day-of-week are restricted, a day matches when EITHER one
    matches. Otherwise the day must satisfy both (an unrestricted field matches
    every day). The month, hour and minute fields must always match.

    `after` and the result use the format "YYYY-MM-DDTHH:MM" (years 0001-9999,
    proleptic Gregorian calendar, no time zones). Return None if no matching
    minute exists after `after` and on or before 9999-12-31T23:59 (some
    expressions, like "0 0 30 2 *", never match).

    Raise ValueError for a malformed expression, a value outside its field's
    range, N > M, a step of 0, or a malformed or impossible `after`.

    >>> cron_next("30 9 * * 1-5", "2024-06-07T09:30")
    '2024-06-10T09:30'
    >>> cron_next("0 0 13 * 5", "2024-09-01T00:00")
    '2024-09-06T00:00'
    """
```
