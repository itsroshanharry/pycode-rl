```python
def normalize_uuid(text: str) -> str:
    """Return the canonical form of a UUID: 32 lowercase hex digits in groups 8-4-4-4-12.

    Exactly these input forms are accepted (hex digits in either case):
    - hyphenated: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" (hyphens only at those
      four positions);
    - hyphenated inside braces: "{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}";
    - "urn:uuid:" (the prefix in any letter case) followed by the hyphenated form;
    - 32 hex digits with no hyphens at all.
    Anything else raises ValueError, including surrounding whitespace, hyphens in
    other positions, braces around the 32-digit form or around the urn form,
    unbalanced braces, or a wrong number of digits.

    >>> normalize_uuid("{123E4567-E89B-12D3-A456-426614174000}")
    '123e4567-e89b-12d3-a456-426614174000'
    >>> normalize_uuid("123e4567e89b12d3a456426614174000")
    '123e4567-e89b-12d3-a456-426614174000'
    """
```
