```python
def cookies_for(set_cookies: list[str], request_path: str) -> str:
    """Process Set-Cookie headers in order and build the Cookie header for a request path
    (a simplified RFC 6265, one host, no expiry by time).

    Parsing one Set-Cookie string: split it on ";". The first part is
    "name=value", split at the FIRST "="; strip spaces/tabs around the name
    and the value. If there is no "=" or the name is empty, ignore the whole
    header. Each later part is an attribute "attr" or "attr=value" (attribute
    names case-insensitive, names and values stripped):
    - Path: if the value is empty or does not start with "/", the path is "/".
      Without a Path attribute the path is also "/". If Path appears several
      times, the LAST one counts.
    - Max-Age: if its value is an optional "-" followed by 1+ ASCII digits and
      is <= 0, the header DELETES the stored cookie with the same (name, path)
      (if any) and stores nothing. Other Max-Age values are ignored.
    - Other attributes are ignored.

    Storage: a cookie is identified by (name, path). Storing an existing one
    replaces its value but keeps its ORIGINAL creation order.

    A cookie path matches `request_path` if they are equal, or the cookie path
    is a prefix of it and either the cookie path ends with "/" or the next
    character of the request path is "/" (so "/docs" matches "/docs/x" but not
    "/docsx"). `request_path` must start with "/", else ValueError.

    Return the matching cookies as "name=value" joined by "; ", ordered by
    longer path first, then by creation order. Return "" if none match.

    >>> cookies_for(["a=1; Path=/docs", "b=2", "c=3; Path=/docs/api", "d=4; path=/doc"], "/docs/api/v1")
    'c=3; a=1; b=2'
    """
```
