_ALLOWED = set("123456789.")


def _units(r: int, c: int):
    """(name, cells) for every unit containing (r, c), in the reporting order."""
    yield "row", [(r, j) for j in range(9)]
    yield "column", [(i, c) for i in range(9)]
    br, bc = 3 * (r // 3), 3 * (c // 3)
    yield "box", [(br + i, bc + j) for i in range(3) for j in range(3)]
    if r == c:
        yield "diagonal", [(i, i) for i in range(9)]
    if r + c == 8:
        yield "anti-diagonal", [(i, 8 - i) for i in range(9)]


def sudoku_check(grid: list[str]) -> tuple[int, int, list[str]] | None:
    if len(grid) != 9 or any(type(row) is not str or len(row) != 9 or not set(row) <= _ALLOWED for row in grid):
        raise ValueError("grid must be 9 rows of 9 characters from 1-9 and '.'")
    for r in range(9):
        for c in range(9):
            v = grid[r][c]
            if v == ".":
                continue
            rules = [name for name, cells in _units(r, c)
                     if any((i, j) != (r, c) and grid[i][j] == v for i, j in cells)]
            if rules:
                return r, c, rules
    return None
