```python
def flatten(obj: dict) -> dict:
    """Flatten nested dicts and lists into a single-level dict of paths.

    Keys of nested dicts are joined with "." and list positions are appended as
    "[i]": {"a": {"b": [10, {"c": 1}]}} becomes {"a.b[0]": 10, "a.b[1].c": 1}.
    Anything that is not a dict or a list is a leaf and is kept as it is (tuples
    are leaves). An empty dict or empty list nested inside is also a leaf, kept as
    {} or [] under its path. An empty top-level dict gives {}.
    Output entries are in depth-first order: dict items in their insertion order,
    list items by index.
    Raise TypeError if `obj` is not a dict. Raise ValueError if any dict key is not
    a non-empty str, or contains ".", "[" or "]".

    >>> flatten({"a": {"b": [10, {"c": 1}]}, "d": None})
    {'a.b[0]': 10, 'a.b[1].c': 1, 'd': None}
    >>> flatten({"x": [], "y": {}, "z": [[1]]})
    {'x': [], 'y': {}, 'z[0][0]': 1}
    """
```
