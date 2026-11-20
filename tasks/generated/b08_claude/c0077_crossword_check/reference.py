import re


def _runs(line: str):
    """(start index, text) for every maximal letter run of length >= 2."""
    for m in re.finditer(r"[A-Z]{2,}", line):
        yield m.start(), m.group()


def crossword_check(grid: list[str], words: list[str]) -> list[tuple[str, int, int, str]]:
    if not grid:
        return []
    width = len(grid[0])
    if width == 0 or any(len(row) != width for row in grid) or any(not re.fullmatch(r"[A-Z#]+", row) for row in grid):
        raise ValueError("bad grid")
    dictionary = {w.upper() for w in words}
    bad = []
    for r, row in enumerate(grid):
        for c, word in _runs(row):
            if word not in dictionary:
                bad.append((r, c, "across", word))
    for c in range(width):
        column = "".join(row[c] for row in grid)
        for r, word in _runs(column):
            if word not in dictionary:
                bad.append((r, c, "down", word))
    bad.sort()  # row, col, then "across" < "down"
    return [(d, r, c, w) for r, c, d, w in bad]
