```python
def compress_ranges(nums: list[int]) -> str:
    """Summarize a collection of integers as a compact string.

    Duplicates are ignored and values are sorted ascending. Every maximal run of
    consecutive integers of length 3 or more is written as "start..end"; values in
    shorter runs are written individually. Items are joined with ",".
    Return "" for an empty list.

    >>> compress_ranges([5, 1, 2, 3, 3, 9, 10])
    '1..3,5,9,10'
    >>> compress_ranges([-2, -1, 0, 4])
    '-2..0,4'
    """
```
