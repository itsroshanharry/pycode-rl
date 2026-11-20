```python
def sudoku_check(grid: list[str]) -> tuple[int, int, list[str]] | None:
    """Check a partially filled "X-Sudoku" grid and report the first conflicting cell.

    `grid` is 9 strings of 9 characters each; a character is an ASCII digit
    "1"-"9" or "." for an empty cell. Rows and columns are numbered 0-8.
    The units are:
      "row"           the 9 cells of a row,
      "column"        the 9 cells of a column,
      "box"           the nine 3x3 boxes (rows 0-2/3-5/6-8 x columns 0-2/3-5/6-8),
      "diagonal"      the cells with row == column,
      "anti-diagonal" the cells with row + column == 8.
    A filled cell CONFLICTS in a unit if another cell of that same unit holds the
    same digit. Return (row, col, rules) for the first conflicting cell in
    row-major order (row 0 left to right, then row 1, ...), where rules lists
    every unit in which that cell conflicts, in the order row, column, box,
    diagonal, anti-diagonal. Return None if no cell conflicts. Empty cells
    never conflict.
    Raise ValueError if the grid is not 9 strings of 9 allowed characters.

    >>> sudoku_check(["5........", ".........", "..5......", ".........", ".........", ".........", ".........", ".........", "........."])
    (0, 0, ['box', 'diagonal'])
    """
```
