```python
def top_k_per_group(rows: list[tuple[str, str, int]], k: int) -> dict[str, list[str]]:
    """For every group, the names of its k best rows.

    Each row is (group, name, score). Within a group, rank rows by score from
    highest to lowest; rows with equal scores are ranked by name in ascending
    order (plain string comparison); rows identical in both score and name keep
    their input order, and duplicates count as separate rows.
    Return a dict mapping every group that appears in `rows` to the list of names
    of its first k ranked rows (all of them if the group has fewer than k rows).
    Groups appear in the dict in the order of their first appearance in `rows`.
    k == 0 gives an empty list for every group. Raise ValueError if k is negative.

    >>> top_k_per_group([("a", "x", 5), ("b", "y", 1), ("a", "w", 5), ("a", "z", 9)], 2)
    {'a': ['z', 'w'], 'b': ['y']}
    """
```
