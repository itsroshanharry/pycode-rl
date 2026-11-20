```python
def word_diff(a: str, b: str) -> list[tuple[str, str]]:
    """Word-level diff of two texts as keep / delete / insert operations.

    The words of a text are the result of str.split() (split on any run of
    whitespace). Let A and B be the word lists, and let LCS(i, j) be the
    length of a longest common subsequence of A[i:] and B[j:] (words compared
    exactly, case-sensitively).

    Build the operations from the start, with i = j = 0:
    - if both lists have words left and A[i] == B[j]: ("=", A[i]), advance both;
    - otherwise, if B is used up, OR (A has words left and
      LCS(i + 1, j) >= LCS(i, j + 1)): ("-", A[i]), advance i  (deletions win ties);
    - otherwise: ("+", B[j]), advance j.
    Stop when both lists are used up. The result keeps as many words as
    possible ("=" count == LCS(0, 0)). Texts have at most 300 words each.

    >>> word_diff("the quick brown fox", "the slow brown dog")
    [('=', 'the'), ('-', 'quick'), ('+', 'slow'), ('=', 'brown'), ('-', 'fox'), ('+', 'dog')]
    """
```
