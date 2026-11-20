import random

import pytest
from solution import sudoku_check

E = "." * 9


def _oracle(grid):
    # independent: precompute, for every unit, which cells have a duplicate digit
    bad = {}
    units = []
    for i in range(9):
        units.append(("row", [(i, j) for j in range(9)]))
        units.append(("column", [(j, i) for j in range(9)]))
        units.append(("box", [(3 * (i // 3) + a, 3 * (i % 3) + b) for a in range(3) for b in range(3)]))
    units.append(("diagonal", [(i, i) for i in range(9)]))
    units.append(("anti-diagonal", [(i, 8 - i) for i in range(9)]))
    for name, cells in units:
        digits = [grid[r][c] for r, c in cells]
        for (r, c), d in zip(cells, digits):
            if d != "." and digits.count(d) > 1:
                bad.setdefault((r, c), set()).add(name)
    if not bad:
        return None
    order = ["row", "column", "box", "diagonal", "anti-diagonal"]
    r, c = min(bad)
    return r, c, [n for n in order if n in bad[(r, c)]]


def _g(*rows):
    rows = [r.ljust(9, ".") for r in rows] + [E] * (9 - len(rows))  # pad short rows with empty cells
    return rows


CASES = [
    _g("5" + "." * 8, E, "..5" + "." * 6),
    _g(),
    _g("12345678."),
    _g("1.......1"),
    _g("1", "1"),
    _g("1" + "." * 7, ".1"),
    _g("........1", E, E, E, E, E, E, E, "1........"),
    _g(".2.......", E, E, E, E, E, E, E, ".2......."),
    _g("....3....", E, E, E, "....3...."),
    _g(E, E, E, E, "....7....", E, E, E, "........7"),
    _g(E, E, E, E, "....7....", E, E, E, "7........"),
    _g(E, ".9.......", E, E, E, E, E, ".......9."),
    _g("534678912", "672195348", "198342567", "859761423", "426853791", "713924856", "961537284", "287419635", "345286179"),
    _g(E, E, "......8..", E, E, E, "..8......"),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], (0, 0, ["box", "diagonal"])),
    (CASES[1], None),
    (CASES[3], (0, 0, ["row"])),
    (CASES[6], (0, 8, ["anti-diagonal"])),
    (CASES[9], (4, 4, ["diagonal"])),
    (CASES[10], (4, 4, ["anti-diagonal"])),
    (CASES[12], (0, 0, ["diagonal"])),
]


@pytest.mark.parametrize("grid", CASES)
def test_against_oracle(grid):
    got = sudoku_check(grid)
    assert (None if got is None else (got[0], got[1], list(got[2]))) == _oracle(grid)


@pytest.mark.parametrize("grid, expected", FIXED)
def test_fixed(grid, expected):
    got = sudoku_check(grid)
    assert (None if got is None else (got[0], got[1], list(got[2]))) == expected


@pytest.mark.parametrize(
    "grid",
    [[E] * 8, [E] * 10, [E] * 8 + ["." * 8], [E] * 8 + ["." * 10], [E] * 8 + ["0........"], [E] * 8 + ["x........"],
     [E] * 8 + ["１........"], [E] * 8 + [" ........"]],
)
def test_invalid(grid):
    with pytest.raises(ValueError):
        sudoku_check(grid)


def test_random_against_oracle():
    rng = random.Random(69)
    for _ in range(400):
        grid = ["".join(rng.choice("123456789" + "." * 12) for _ in range(9)) for _ in range(9)]
        got = sudoku_check(grid)
        assert (None if got is None else (got[0], got[1], list(got[2]))) == _oracle(grid)
