```python
def percentile(values: list[int], p: str, method: str) -> str:
    """The p-th percentile of integer values, under a named convention.

    Sort the values: x[0] <= ... <= x[n-1]. Let h = (n - 1) * p / 100 (exact),
    lo = floor(h), hi = ceil(h). Methods:
      "linear":   x[lo] + (h - lo) * (x[hi] - x[lo])
      "lower":    x[lo]
      "higher":   x[hi]
      "nearest":  x[round(h)], where an exact .5 rounds to the EVEN index
      "midpoint": (x[lo] + x[hi]) / 2
    `p` is a string: 0-100 with optional decimals ("50", "2.5", "99.99",
    "100.0"); it must not exceed 100.
    Compute exactly (no floats) and return the result rounded to 6 decimal
    places (ties to even) as a string with exactly 6 decimals; never "-0.000000".
    Raise ValueError for empty values, an unknown method, or a bad p.

    >>> percentile([15, 20, 35, 40, 50], "40", "linear")
    '29.000000'
    >>> percentile([1, 2, 3, 4], "50", "nearest")
    '3.000000'
    """
```
