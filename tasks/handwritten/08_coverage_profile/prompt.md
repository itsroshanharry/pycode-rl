```python
def coverage_profile(intervals: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    """Total weight covering each point of the number line, as segments.

    Each interval (start, end, weight) adds the integer `weight` to every point of
    the half-open range [start, end), where start < end; weights may be negative.
    Return the piecewise-constant total as a sorted list of non-overlapping
    segments (start, end, total), including only ranges where the total is
    non-zero. Adjacent segments with equal totals must be merged into one.

    >>> coverage_profile([(0, 5, 1), (3, 8, 2)])
    [(0, 3, 1), (3, 5, 3), (5, 8, 2)]
    >>> coverage_profile([(0, 2, 1), (2, 4, 1)])
    [(0, 4, 1)]
    """
```
