```python
def apply_hunk(lines: list[str], hunk: list[str]) -> list[str]:
    """Apply one unified-diff hunk to a file given as a list of lines.

    hunk[0] is a header "@@ -A,B +C,D @@" where A, B, C, D are non-negative
    integers; ",B" or ",D" may be omitted, meaning 1. Anything after the second "@@"
    is ignored. Every following entry starts with " " (context line), "-" (removed
    line) or "+" (added line), and the rest of the entry is the line's text.
    The old part (context and removed lines, in order) must equal the file's lines
    starting at line A (1-based); if B == 0 the hunk removes nothing and its added
    lines go right after line A (A == 0 means at the very start). Replace that old
    part with the new part (context and added lines, in order) and return the result.
    Raise ValueError if the header is malformed, an entry has another prefix, the
    number of old lines differs from B or of new lines from D, or the old part does
    not match the file at that position. Do not search other positions.

    >>> apply_hunk(["a", "b", "c"], ["@@ -2,1 +2,2 @@", "-b", "+B", "+B2"])
    ['a', 'B', 'B2', 'c']
    >>> apply_hunk(["x"], ["@@ -0,0 +1 @@ top", "+new"])
    ['new', 'x']
    """
```
