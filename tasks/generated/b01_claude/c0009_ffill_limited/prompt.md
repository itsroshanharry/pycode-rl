```python
def ffill_limited(values: list, limit: int) -> list:
    """Forward-fill missing values (None) in a series, at most `limit` in a row.

    Each None is replaced by the most recent non-None value before it, but within
    any run of consecutive Nones only the first `limit` are filled; the rest of
    that run stays None. Nones before the first non-None value stay None.
    Non-None values (ints, floats or strings, including 0, 0.0, "" and False) are
    real values: they are kept and can be used for filling.
    limit >= 0 (0 fills nothing); raise ValueError if limit is negative.
    Return the filled list, the same length as `values`.

    >>> ffill_limited([1, None, None, None, 5, None], 2)
    [1, 1, 1, None, 5, 5]
    >>> ffill_limited([None, 0, None], 1)
    [None, 0, 0]
    """
```
