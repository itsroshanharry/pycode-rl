```python
def freshness(headers: dict[str, str], shared: bool) -> int | None:
    """Freshness lifetime, in seconds, of an HTTP response (a simplified RFC 9111).

    Header names in `headers` are case-insensitive; two keys that differ only
    in case are a ValueError. The relevant headers are Cache-Control, Date and
    Expires.

    Cache-Control is a comma-separated list. Spaces/tabs around elements are
    ignored and empty elements are skipped. Each element is a directive name
    (a token: one or more of A-Z a-z 0-9 ! # $ % & ' * + - . ^ _ ` | ~),
    compared case-insensitively, optionally followed by "=" and a value that is
    either a token or a quoted string ('"' + any characters except '"' and
    backslash + '"'; commas inside quotes do not split elements). No spaces are
    allowed around "=". Anything else makes Cache-Control malformed: ValueError.

    Rules, first match wins:
    1. "no-cache" WITHOUT a value -> 0. (With a value, e.g. no-cache="Set-Cookie",
       it is ignored here.)
    2. Only if `shared`: if "s-maxage" is present, use it (see below).
    3. If "max-age" is present, use it.
    4. If Expires is present: if it is not a valid date, 0; otherwise, if Date is
       missing or not a valid date, None; otherwise max(0, Expires - Date).
    5. Otherwise None.
    Using s-maxage or max-age: if the directive appears more than once, or its
    value is missing or is not 1+ ASCII digits (after removing quotes, so
    max-age="60" is 60), the lifetime is 0. Values above 2147483648 are capped
    at 2147483648.

    A valid date is an IMF-fixdate such as "Sun, 06 Nov 1994 08:49:37 GMT":
    exactly that layout, English day and month abbreviations with that
    capitalization, a real calendar date and time (seconds 00-59), and the day
    name must be the correct weekday.

    >>> freshness({"Cache-Control": "public, max-age=600, s-maxage=60"}, shared=True)
    60
    >>> freshness({"date": "Sun, 06 Nov 1994 08:49:37 GMT", "EXPIRES": "Sun, 06 Nov 1994 09:49:37 GMT"}, shared=False)
    3600
    """
```
