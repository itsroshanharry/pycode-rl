```python
def parse_duration(text: str) -> int:
    """Convert a duration such as "1h30m" or "2d 4h 5s" into total seconds.

    The text is one or more components "<digits><unit>", where digits are ASCII
    0-9 and the unit is d (86400 s), h (3600 s), m (60 s) or s (1 s), written in
    lowercase directly after its number. Each unit may appear at most once and
    units must appear in the order d, h, m, s. Components may be separated by
    spaces, and leading/trailing spaces are allowed.
    Raise ValueError for anything else (empty text, unknown unit, missing number,
    repeated or out-of-order unit, signs, decimals, a space between a number and
    its unit, other separators).

    >>> parse_duration("1h30m")
    5400
    >>> parse_duration(" 2d 4h 5s ")
    187205
    """
```
