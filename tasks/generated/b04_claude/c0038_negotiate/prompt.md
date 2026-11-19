```python
def negotiate(accept: str, offered: list[str]) -> str | None:
    """Choose the best media type from `offered` for an HTTP Accept header.

    `accept` is a comma-separated list of elements. Spaces and tabs around an
    element, around each ";" and around the media range are ignored, and empty
    elements are skipped. A header with no non-empty element means "*/*".

    Each element is a media range followed by zero or more ";name=value" parameters.
    - A media range is "type/subtype", "type/*" or "*/*", where type and subtype
      are tokens: one or more of A-Z a-z 0-9 ! # $ % & ' * + . ^ _ ` | ~ -
      "*/subtype" is not allowed. Types are compared case-insensitively.
    - Parameter names and values are tokens, with no whitespace around "=".
      Only the "q" parameter (name case-insensitive) matters; other parameters
      are ignored. A q value must match 0(\.[0-9]{0,3})? or 1(\.0{0,3})?
      ("0", "0.", "0.5", "0.125", "1", "1.000"); a missing q means 1.
      An element may have at most one q parameter.

    Each offered entry is a concrete "type/subtype". Its quality is the q of the
    MOST SPECIFIC kind of range that matches it: an exact "type/subtype" range
    beats "type/*", which beats "*/*", even if the more specific one has a lower q.
    If several ranges of that kind match, use the highest of their q values.
    No matching range means quality 0.

    Return the offered entry (exactly as given) with the highest quality; ties go
    to the entry that comes first in `offered`. Return None if no entry has a
    quality above 0 (including when `offered` is empty).
    Raise ValueError if `accept` is malformed.

    >>> negotiate("text/html;q=0.8, application/json", ["text/html", "application/json"])
    'application/json'
    >>> negotiate("text/*;q=0.5, text/plain;q=0", ["text/plain", "text/csv"])
    'text/csv'
    """
```
