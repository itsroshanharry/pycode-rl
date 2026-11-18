```python
def parse_query(query: str) -> dict[str, list[str]]:
    """Parse a URL query string into a dict mapping each key to its list of values.

    The query (without a leading "?") is split on "&"; empty segments are ignored.
    Each segment is "key=value", or just "key" meaning the value "". Only the first
    "=" separates key and value (later ones belong to the value). In keys and
    values, "+" means a space and "%XY" (X, Y hex digits, either case) is one byte;
    the resulting bytes are decoded as UTF-8 (other characters stand for
    themselves). Repeated keys collect their values in order, and keys appear in the
    order they first occur.
    Raise ValueError for a "%" not followed by two hex digits, for bytes that are not
    valid UTF-8, or for an empty key (as in "=x").

    >>> parse_query("a=1&b=two+words&a=%E2%82%AC")
    {'a': ['1', '€'], 'b': ['two words']}
    >>> parse_query("flag&x=&&y==z")
    {'flag': [''], 'x': [''], 'y': ['=z']}
    """
```
