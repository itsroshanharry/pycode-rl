```python
def wrap_text(text: str, width: int) -> list[str]:
    """Greedy word wrap.

    Words are maximal runs of non-whitespace characters. A word longer than
    `width` is first split into chunks of exactly `width` characters (the last
    chunk may be shorter); each chunk is then treated as a separate word. Lines are
    filled greedily in order: each line holds as many consecutive words as fit,
    separated by single spaces, with total length <= width. Return the list of
    lines; an empty or whitespace-only text gives []. width >= 1.

    >>> wrap_text("the quick brown fox", 10)
    ['the quick', 'brown fox']
    >>> wrap_text("abcdefghij kl", 4)
    ['abcd', 'efgh', 'ij', 'kl']
    """
```
