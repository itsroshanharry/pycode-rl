```python
def parse_fixed_width(record: str, layout: list[tuple[str, int, int, str]]) -> dict:
    """Parse one fixed-width record using a column layout.

    Each layout entry is (name, start, width, kind). `start` is the 1-BASED
    column of the field's first character, so the field is
    record[start - 1 : start - 1 + width]. Fields may overlap. The record must
    be at least as long as the furthest field end (longer is fine).

    Kinds:
    - "str":  remove trailing SPACES only (not tabs or other whitespace) and
              leading nothing; the result may be "".
    - "int":  optional leading spaces, then an optional "-", then 1+ ASCII
              digits (leading zeros allowed), then optional trailing spaces.
              A field of only spaces is None.
    - "cents": like "int", but the digits carry 2 implied decimals; return the
              value as a string "<int>.<2 digits>" ("-0012345" -> "-123.45",
              "5" -> "0.05"). Only spaces -> None.
    - "date": "YYYYMMDD" -> "YYYY-MM-DD"; it must be a real date. "00000000"
              or only spaces -> None.
    - "flag": "Y" -> True, "N" -> False, a single space -> None (width must be 1).
    Return {name: value} in layout order.

    Raise ValueError for a too-short record, start < 1, width < 1, an unknown
    kind, a duplicate name, or a field whose text does not fit its kind.

    >>> parse_fixed_width("ACME      -001234520240229Y", [("name", 1, 10, "str"), ("amount", 11, 8, "cents"), ("day", 19, 8, "date"), ("ok", 27, 1, "flag")])
    {'name': 'ACME', 'amount': '-123.45', 'day': '2024-02-29', 'ok': True}
    """
```
