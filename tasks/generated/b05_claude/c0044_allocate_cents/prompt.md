```python
def allocate_cents(total: int, weights: list[int]) -> list[int]:
    """Split an integer number of cents into parts proportional to `weights`.

    Part i's ideal share is total * weights[i] / sum(weights), as an exact
    fraction (no floating point).
    For total >= 0: each part first gets the floor of its ideal share; the cents
    still left over are handed out one each to the parts with the LARGEST
    fractional remainder. Ties go to the part with the larger weight, then to
    the earlier part.
    For total < 0: allocate -total in the same way and negate every part, so a
    refund mirrors the original charge.
    The parts therefore always sum to `total`.

    Raise ValueError if `weights` is empty, any weight is negative, or all
    weights are 0.

    >>> allocate_cents(100, [1, 1, 1])
    [34, 33, 33]
    >>> allocate_cents(-100, [1, 1, 1])
    [-34, -33, -33]
    >>> allocate_cents(2, [1, 3])
    [0, 2]
    """
```
