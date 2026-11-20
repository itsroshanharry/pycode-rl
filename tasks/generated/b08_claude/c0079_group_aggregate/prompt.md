```python
def group_aggregate(rows: list[dict], keys: list[str], value: str) -> list[tuple]:
    """Group rows by several key columns and aggregate one value column.

    Each row is a dict. A row's group is the tuple of row.get(k) for k in
    `keys` (a missing key counts as None). Within a key column all non-None
    values have the same type (all ints or all strs), so they can be compared.
    For each group compute:
      count = number of rows in the group (ALL rows, even if their value is
              missing or None),
      sum, min, max = over the non-None int values of the `value` column;
              if there are none: sum 0, min None, max None.
    Return one tuple (*group_key, count, sum, min, max) per group, sorted by
    the group key column by column, where None comes BEFORE every other value.
    With keys == [] all rows form one group () (no rows -> []).

    >>> group_aggregate([{"r": "eu", "v": 5}, {"r": None, "v": 1}, {"r": "eu"}, {"v": 7}], ["r"], "v")
    [(None, 2, 8, 1, 7), ('eu', 2, 5, 5, 5)]
    """
```
