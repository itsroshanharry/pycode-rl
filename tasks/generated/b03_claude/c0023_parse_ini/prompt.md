```python
def parse_ini(text: str) -> dict[str, dict[str, str]]:
    """Parse INI-style configuration text into {section: {key: value}}.

    Process the text line by line (lines are separated by newline characters).
    Surrounding whitespace on each line is ignored. Empty lines and lines whose
    first character is ";" or "#" are comments.
    - "[name]" starts a section. The name is trimmed, must be non-empty and must not
      contain "[" or "]". Section names are case-sensitive. A repeated header
      continues the same section.
    - "key = value" sets a key: split at the first "=", then trim both parts. The
      key must be non-empty and is stored in lowercase. A repeated key in the same
      section overwrites the earlier value.
    - In a value, a ";" or "#" that directly follows a whitespace character starts
      an inline comment: it and everything after it are removed, then the value is
      trimmed again. A ";" or "#" with no whitespace before it is part of the value.
    Keys before any section header belong to section "", which appears in the result
    only if it has at least one key. Every other section appears, even if empty.
    Raise ValueError for any other kind of line.

    >>> parse_ini("a=1\n[S]\nx = hello ;greeting\ny=a;b\n[S]\nX = 2")
    {'': {'a': '1'}, 'S': {'x': '2', 'y': 'a;b'}}
    """
```
