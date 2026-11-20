import random

import pytest
from solution import apply_hunk


@pytest.mark.parametrize(
    "lines, hunk, expected",
    [
        (["a", "b", "c"], ["@@ -2,1 +2,2 @@", "-b", "+B", "+B2"], ["a", "B", "B2", "c"]),
        (["x"], ["@@ -0,0 +1 @@ top", "+new"], ["new", "x"]),
        (["a", "b"], ["@@ -2,0 +3 @@", "+c"], ["a", "b", "c"]),
        (["a", "b", "c"], ["@@ -1,0 +2 @@", "+between"], ["a", "between", "b", "c"]),
        (["a", "b", "c"], ["@@ -1,3 +1,2 @@", " a", "-b", " c"], ["a", "c"]),
        (["a", "b", "c"], ["@@ -1,3 +0,0 @@", "-a", "-b", "-c"], []),
        ([], ["@@ -0,0 +1,2 @@", "+x", "+y"], ["x", "y"]),
        (["a", "b"], ["@@ -2 +2 @@", "-b", "+B"], ["a", "B"]),
        (["a", " b", "c"], ["@@ -2,1 +2,1 @@", "-" + " b", "+" + "  b"], ["a", "  b", "c"]),
        (["", "x", ""], ["@@ -1,3 +1,3 @@", " ", "-x", "+y", " "], ["", "y", ""]),
        (["a", "b"], ["@@ -1,2 +1,2 @@ def f():", " a", " b"], ["a", "b"]),
        (["a", "b"], ["@@ -1,1 +1,1 @@", "-a", "+-a"], ["-a", "b"]),
    ],
)
def test_apply(lines, hunk, expected):
    assert list(apply_hunk(lines, hunk)) == expected


@pytest.mark.parametrize(
    "lines, hunk",
    [
        (["a"], ["@@ -1 +1 @@", "-z", "+y"]),
        (["a", "b"], ["@@ -1,2 +1,1 @@", "-a", " b", "+extra"]),
        (["a"], ["@@ -1,1 +1,1 @@", "-a"]),
        (["a"], ["@@ -1,1 +1,1 @@", "*a", "+b"]),
        (["a"], ["@@ -1,1 +1,1", "-a", "+b"]),
        (["a"], ["@@ -x,1 +1,1 @@", "-a", "+b"]),
        (["a"], ["-a", "+b"]),
        (["a", "b"], ["@@ -1,1 +1,1 @@", "-b", "+B"]),
        (["a"], ["@@ -5,1 +5,1 @@", "-a", "+b"]),
        (["a"], []),
        (["a"], ["@@ -1,1 +1,1 @@", "", "+b"]),
        (["a"], ["@@ -1,1 +1,1 @@", "-a", "+b", "*junk"]),
        (["a", "b"], ["@@ -1,2 +1,2 @@", " a", "~x", "-b", "+B"]),
        (["a"], ["@@ -2,0 +2 @@", "+b"]),
        ([], ["@@ -1,0 +1 @@", "+b"]),
    ],
)
def test_invalid(lines, hunk):
    with pytest.raises(ValueError):
        apply_hunk(lines, hunk)


def test_random_round_trip():
    # Make a random edit, write its hunk the way diff does, apply it, compare.
    rng = random.Random(25)
    for _ in range(200):
        lines = [rng.choice(["a", "b", "c", "", " x"]) for _ in range(rng.randint(0, 8))]
        i = rng.randint(0, len(lines))
        k = rng.randint(0, len(lines) - i)
        removed, added = lines[i : i + k], [rng.choice(["N", "M", ""]) for _ in range(rng.randint(0, 3))]
        pre = lines[max(0, i - 1) : i]
        post = lines[i + k : i + k + 1]
        old_block = pre + removed + post
        new_block = pre + added + post
        b = len(old_block)
        a = (i - len(pre) + 1) if b else i
        hunk = [f"@@ -{a},{b} +1,{len(new_block)} @@"] + [" " + t for t in pre] + ["-" + t for t in removed] + ["+" + t for t in added] + [" " + t for t in post]
        expected = lines[:i] + added + lines[i + k :]
        assert list(apply_hunk(lines, hunk)) == expected, (lines, hunk)
