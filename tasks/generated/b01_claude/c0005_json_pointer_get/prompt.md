```python
def json_pointer_get(doc, pointer: str):
    """Return the value inside `doc` that a JSON Pointer refers to.

    `doc` is built from dicts (with str keys), lists, and scalars (str, int, float,
    bool, None). `pointer` is either "" (meaning the whole document) or one or more
    reference tokens, each preceded by "/". Inside a token, "~1" stands for "/" and
    "~0" for "~", read left to right (so "~01" is the two characters "~1"); a "~"
    followed by anything else, or at the end of a token, is invalid.
    Each token is applied to the current value: for a dict it is the key; for a list
    it must be "0" or a decimal integer without leading zeros or sign, less than the
    list's length.
    Errors: ValueError if a non-empty pointer does not start with "/" or has an
    invalid "~" escape (checked before anything is looked up); KeyError for a
    missing dict key; IndexError for a malformed or out-of-range list index;
    TypeError when a token is applied to a scalar.

    >>> json_pointer_get({"a": {"b/c": [10, 20]}}, "/a/b~1c/1")
    20
    >>> json_pointer_get({"": 1}, "/")
    1
    """
```
