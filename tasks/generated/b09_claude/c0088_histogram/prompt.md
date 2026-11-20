```python
def histogram(values: list[str], lo: str, hi: str, width: str) -> tuple[list[int], int, int]:
    """Count decimal values into fixed-width bins between lo and hi.

    All numbers are decimal strings: an optional "-", ASCII digits, and an
    optional "." followed by digits ("0.3", "-12", "7.25"). Work with their
    EXACT decimal values (no floating point: 0.1 + 0.2 == 0.3 here).
    lo < hi and width > 0 are required.

    The bins split [lo, hi] into n = ceil((hi - lo) / width) bins. Bin i covers
    lo + i*width <= x < lo + (i+1)*width, except that the LAST bin also
    includes hi itself and ends at hi (it may be narrower than `width`).
    Values below lo are counted as underflow; values above hi as overflow.

    Return (counts per bin, underflow, overflow).
    Raise ValueError for a malformed number, lo >= hi, or width <= 0.

    >>> histogram(["0", "0.1", "0.2", "0.3", "0.35", "1"], "0", "0.35", "0.1")
    ([1, 1, 1, 2], 0, 1)
    """
```
