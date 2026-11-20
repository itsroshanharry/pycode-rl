```python
def pivot_table(triples: list[tuple[str, str, int]], policy: str, default: int, totals: bool) -> list[list]:
    """Pivot (row, column, value) triples into a table.

    Row labels and column labels are the distinct row/column strings, each
    sorted in plain string order. Several triples for the same (row, column)
    cell are combined by `policy`:
      "sum"   add them;  "max"  take the largest;  "first" keep the one that
      comes first in `triples`;  "last" keep the one that comes last;
      "error" raise ValueError if a cell has more than one triple.
    A cell with no triple shows `default`.

    Output is a list of rows. The first row is the header: "" followed by the
    column labels. Each other row is the row label followed by its cells.
    If `totals` is True, add a final "Total" column (each row's sum) and a final
    "Total" row (each column's sum, and the grand total in the corner). Totals
    add only cells that came from triples: a `default` cell counts as 0 in
    every total, even if `default` is not 0.
    With no triples the table is just the header [""] (plus ["Total", 0] as a
    row and "Total" in the header when totals is True).
    Raise ValueError for an unknown policy.

    >>> pivot_table([("east", "Q1", 5), ("west", "Q1", 3), ("east", "Q2", 2), ("east", "Q1", 1)], "sum", -1, True)
    [['', 'Q1', 'Q2', 'Total'], ['east', 6, 2, 8], ['west', 3, -1, 3], ['Total', 9, 2, 11]]
    """
```
