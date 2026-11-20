```python
def crossword_check(grid: list[str], words: list[str]) -> list[tuple[str, int, int, str]]:
    """Find the entries of a filled crossword grid that are not dictionary words.

    `grid` is a list of rows of equal length (at least 1); each character is
    "#" (a block) or an uppercase ASCII letter A-Z. An entry is a maximal run
    of 2 or more letters in a row (across, read left to right) or in a column
    (down, read top to bottom); single letters are not entries.
    `words` is the dictionary; compare case-insensitively.

    Return every entry that is not in the dictionary as
    (direction, row, col, WORD), where direction is "across" or "down",
    (row, col) is the entry's first cell (0-based) and WORD is uppercase.
    Sort by row, then col, then direction ("across" before "down").
    An empty grid ([]) gives []. Raise ValueError for rows of different
    lengths, an empty row, or any other character.

    >>> crossword_check(["CAT#", "A#OX", "RAT#"], ["cat", "car", "rat", "ox"])
    [('down', 0, 2, 'TOT')]
    """
```
