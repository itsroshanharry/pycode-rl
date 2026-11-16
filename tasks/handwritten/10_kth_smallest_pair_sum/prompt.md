```python
def kth_smallest_pair_sum(a: list[int], b: list[int], k: int) -> int:
    """Return the k-th smallest value among all sums a[i] + b[j].

    Every index pair (i, j) contributes one sum, so equal sums are counted
    separately; k is 1-indexed. The lists are not necessarily sorted and may contain
    negative numbers and duplicates. Raise ValueError if k is not between 1 and
    len(a) * len(b). Each list has at most 2000 elements.

    >>> kth_smallest_pair_sum([1, 7, 11], [2, 4, 6], 3)
    7
    >>> kth_smallest_pair_sum([3, 1], [1, 1], 4)
    4
    """
```
