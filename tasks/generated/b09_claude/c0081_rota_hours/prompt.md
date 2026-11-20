```python
def rota_hours(pattern: list[int], offsets: dict[str, int], first_day: int, last_day: int,
               holidays: list[int]) -> dict[str, str]:
    """Paid hours per worker for a repeating shift rota over a range of days.

    Days are plain integers (they may be negative or very large). `pattern`
    holds the hours worked on each day of the rota cycle (ints 0..24, length
    L >= 1). A worker with offset k is at cycle position (d - k) mod L on day d
    (Python's %, always 0..L-1), so the worker works pattern[(d - k) % L] hours
    that day. Note the MINUS: day k is that worker's position 0.

    Paid hours for a day with h hours worked (applied per day, per worker):
      the first 8 hours count 1x, hours above 8 up to 12 count 1.5x, and hours
      above 12 count 2x  (so 10 h -> 11, 12 h -> 14, 13 h -> 16).
    On a holiday the day's paid hours (after the rule above) are DOUBLED.
    `holidays` may contain duplicates (a day is a holiday or not) and days
    outside the range (ignored).

    Count every day from first_day to last_day INCLUSIVE. Return
    {worker: total paid hours} with the total written with exactly one decimal
    ("123.5", "124.0"). Keys in the same order as `offsets`.

    Limits: last_day - first_day can be up to 10**12, L <= 1000, up to 50
    workers and 5000 holidays, so iterating over every day is far too slow.
    Raise ValueError if first_day > last_day, pattern is empty, or an hour
    value is outside 0..24.

    >>> rota_hours([10, 0, 13], {"ana": 0, "bo": 1}, 0, 5, [2, 2, 99])
    {'ana': '70.0', 'bo': '54.0'}
    """
```
