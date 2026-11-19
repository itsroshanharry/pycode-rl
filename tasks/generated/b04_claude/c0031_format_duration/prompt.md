```python
def format_duration(seconds: int, max_units: int = 2) -> str:
    """Format a number of seconds as a short duration such as "2h 5m".

    The units, largest first, are d (86400 s), h (3600 s), m (60 s) and s (1 s).
    Only a window of `max_units` consecutive units is used, starting at the largest
    unit that is not bigger than `seconds` (the window simply stops after "s").
    Round `seconds` half up to a whole number of the window's smallest unit. If
    rounding reaches the next larger unit (e.g. 59.5 minutes becomes 1 hour), start
    again with the rounded value. Then write each unit of the window with its value,
    largest first, as "<value><unit>" joined by single spaces, leaving out units
    whose value is 0. Zero seconds is "0s".
    Raise ValueError if seconds < 0 or max_units < 1.

    >>> format_duration(3725)
    '1h 2m'
    >>> format_duration(86399)
    '1d'
    """
```
