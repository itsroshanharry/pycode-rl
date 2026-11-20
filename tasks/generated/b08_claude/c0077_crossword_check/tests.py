import random

import pytest
from solution import crossword_check


@pytest.mark.parametrize(
    "grid, words, expected",
    [
        (["CAT#", "A#OX", "RAT#"], ["cat", "car", "rat", "ox"], [("down", 0, 2, "TOT")]),
        ([], ["a"], []),
        (["A"], [], []),
        (["#"], [], []),
        (["AB"], [], [("across", 0, 0, "AB")]),
        (["A", "B"], [], [("down", 0, 0, "AB")]),
        (["AB"], ["Ab"], []),
        (["AB", "CD"], ["ab"], [("down", 0, 0, "AC"), ("down", 0, 1, "BD"), ("across", 1, 0, "CD")]),
        (["AB", "CD"], [], [("across", 0, 0, "AB"), ("down", 0, 0, "AC"), ("down", 0, 1, "BD"), ("across", 1, 0, "CD")]),
        (["A#B"], [], []),
        (["AB#CD"], ["ab"], [("across", 0, 3, "CD")]),
        (["#AB", "#CD"], [], [("across", 0, 1, "AB"), ("down", 0, 1, "AC"), ("down", 0, 2, "BD"), ("across", 1, 1, "CD")]),
        (["X#", "Y#", "#Z", "#Q"], ["xy"], [("down", 2, 1, "ZQ")]),
        (["HELLO", "#####", "WORLD"], ["hello", "world"], []),
        (["HELLO", "#####", "WORLD"], ["hello"], [("across", 2, 0, "WORLD")]),
    ],
)
def test_examples(grid, words, expected):
    assert [tuple(x) for x in crossword_check(grid, words)] == expected


@pytest.mark.parametrize("grid", [["AB", "C"], [""], ["ab"], ["A.B"], ["A B"], ["ÄB"], ["AB", ""], ["A1"]])
def test_invalid(grid):
    with pytest.raises(ValueError):
        crossword_check(grid, [])


def _oracle(grid, words):
    d = {w.upper() for w in words}
    h, w = len(grid), len(grid[0])
    out = []
    for r in range(h):
        for c in range(w):
            if grid[r][c] == "#":
                continue
            if (c == 0 or grid[r][c - 1] == "#") and c + 1 < w and grid[r][c + 1] != "#":
                e = c
                while e < w and grid[r][e] != "#":
                    e += 1
                word = grid[r][c:e]
                if word not in d:
                    out.append(("across", r, c, word))
            if (r == 0 or grid[r - 1][c] == "#") and r + 1 < h and grid[r + 1][c] != "#":
                e = r
                while e < h and grid[e][c] != "#":
                    e += 1
                word = "".join(grid[k][c] for k in range(r, e))
                if word not in d:
                    out.append(("down", r, c, word))
    return out


def test_random_against_oracle():
    rng = random.Random(67)
    for _ in range(300):
        h, w = rng.randint(1, 6), rng.randint(1, 6)
        grid = ["".join(rng.choice("AB#") for _ in range(w)) for _ in range(h)]
        words = rng.sample(["AB", "BA", "aa", "bb", "ABA", "bab", "AAB"], rng.randint(0, 5))
        assert [tuple(x) for x in crossword_check(grid, words)] == _oracle(grid, words), (grid, words)
