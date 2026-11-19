```python
def toc_numbers(headings: list[tuple[int, str]]) -> list[str]:
    """Number document headings like a table of contents.

    Each heading is (level, title) with an int level from 1 to 6, in document order.
    A heading's parent is the nearest earlier heading with a strictly smaller level;
    a heading with no such earlier heading is top-level. Headings with the same
    parent are siblings, numbered 1, 2, 3, ... in order. A top-level heading's
    number is its position among top-level headings ("1", "2", ...); any other
    heading's number is its parent's number, a ".", and its position among its
    siblings ("2.1", "2.1.3"). Levels may skip (a level-3 heading right under a
    level-1 heading is simply its child).
    Return "<number> <title>" for each heading, in order.
    Raise ValueError if a level is not an int from 1 to 6.

    >>> toc_numbers([(1, "Intro"), (2, "Goals"), (2, "Scope"), (1, "Design"), (3, "Detail"), (2, "API")])
    ['1 Intro', '1.1 Goals', '1.2 Scope', '2 Design', '2.1 Detail', '2.2 API']
    """
```
