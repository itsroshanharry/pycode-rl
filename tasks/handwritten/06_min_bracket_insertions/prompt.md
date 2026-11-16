```python
def min_bracket_insertions(s: str) -> int:
    """Minimum number of bracket characters to insert into `s` so that it becomes
    a balanced bracket sequence.

    `s` consists only of the characters ()[]{} and has length at most 40. A
    sequence is balanced if it is empty, a concatenation of two balanced sequences,
    or an opening bracket followed by a balanced sequence and the matching closing
    bracket. Characters may be inserted at any positions; existing characters may
    not be removed or changed.

    >>> min_bracket_insertions("(]")
    2
    >>> min_bracket_insertions("([)]")
    2
    """
```
