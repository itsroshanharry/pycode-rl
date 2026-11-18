```python
def natural_sort(names: list[str]) -> list[str]:
    """Sort file names in natural order ("file2" before "file10").

    Split each name into maximal runs of ASCII digits (0-9) and maximal runs of
    other characters. Compare two names run by run from the left:
    - two digit runs compare by numeric value;
    - two non-digit runs compare case-insensitively, using str.casefold();
    - a digit run sorts before a non-digit run.
    If all compared runs are equal and one name has fewer runs, it sorts first.
    Names that are still equal (such as "a01" vs "a1", or "A" vs "a") are ordered
    by plain string comparison (Python's < on str). Exactly equal names keep their
    input order. Non-ASCII digits (such as "٣") are ordinary characters, not digits.

    >>> natural_sort(["file10.txt", "file2.txt", "File1.txt"])
    ['File1.txt', 'file2.txt', 'file10.txt']
    >>> natural_sort(["a1", "a01", "a001"])
    ['a001', 'a01', 'a1']
    """
```
