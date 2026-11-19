```python
def parse_dotenv(text: str) -> dict[str, str]:
    r"""Parse the contents of a .env file into a dict of variables.

    Process line by line (split on "\n"). Skip lines that are empty or contain only
    whitespace, and lines whose first non-whitespace character is "#".
    Every other line is: optional leading whitespace, an optional "export" followed by
    at least one space, a NAME, optional spaces, "=", optional spaces, then a VALUE.
    NAME is an ASCII letter or "_" followed by ASCII letters, digits or "_".
    VALUE forms:
    - single-quoted 'text': taken literally (no escapes); must close on the same line;
    - double-quoted "text": the escapes \n (newline), \t (tab), \" and \\ are
      decoded; any other backslash sequence is an error; must close on the same line;
    - unquoted: everything up to the first " #" (space then "#"), which starts a
      comment, with trailing whitespace removed (an empty unquoted value is "").
    After a closing quote, only whitespace and an optional comment starting with "#"
    may follow. A later assignment to the same NAME replaces the earlier one.
    Raise ValueError for any malformed line.

    >>> parse_dotenv('export A=1 # one\nB="x\\ty"\nC=\'$HOME\'\nA=2')
    {'A': '2', 'B': 'x\ty', 'C': '$HOME'}
    """
```
