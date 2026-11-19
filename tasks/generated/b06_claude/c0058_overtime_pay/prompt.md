```python
def overtime_pay(daily_minutes: list[int], rate_cents: int) -> int:
    """Gross pay in cents for one work week with daily, weekly and seventh-day overtime.

    `daily_minutes` has exactly 7 entries (Monday .. Sunday), each the
    number of minutes worked that day, 0..1440. `rate_cents` is the base
    hourly rate in cents (>= 0).

    Every worked minute earns rate_cents / 60 times a multiplier. The
    multiplier is the HIGHEST that applies (multipliers never add or stack):
    - daily: 1.0 for the day's minutes 1-480, 1.5 for minutes 481-720,
      2.0 for minutes beyond 720;
    - weekly: 1.5 for every minute after the first 2400 minutes of the week
      (counting all minutes Monday -> Sunday, in order);
    - seventh day: only if all seven days have some work, then on Sunday
      every minute is at least 1.5, and Sunday minutes beyond 480 are 2.0.

    Compute the exact total and round it to whole cents only once, at the
    end, with halves rounded up.
    Raise ValueError if there are not exactly 7 entries, an entry is outside
    0..1440, or rate_cents < 0.

    >>> overtime_pay([600, 600, 600, 600, 600, 0, 0], 6000)
    354000
    >>> overtime_pay([60] * 7, 6000)
    45000
    """
```
