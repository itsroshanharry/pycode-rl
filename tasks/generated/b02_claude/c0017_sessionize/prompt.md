```python
def sessionize(events: list[tuple[str, int]], gap: int) -> list[tuple[str, int, int, int]]:
    """Group click events into per-user sessions.

    Each event is (user, timestamp_seconds). Events arrive in no particular order,
    and identical events may repeat (each one counts). For each user, take their
    timestamps in increasing order: a new session starts whenever the time since
    that user's previous event is greater than `gap` seconds (a difference of
    exactly `gap` stays in the same session).
    Return one tuple (user, start, end, event_count) per session, sorted by start
    time, then by user name. gap >= 0; raise ValueError if gap is negative.

    >>> sessionize([("a", 10), ("b", 5), ("a", 100), ("a", 40)], 30)
    [('b', 5, 5, 1), ('a', 10, 40, 2), ('a', 100, 100, 1)]
    """
```
