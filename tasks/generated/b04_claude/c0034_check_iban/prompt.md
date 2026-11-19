```python
def check_iban(iban: str, lengths: dict[str, int]) -> str:
    """Validate an IBAN and report the first problem found.

    First remove every space character (" "); nothing else is ignored. Then apply
    these checks in order and return the name of the first one that fails:
    1. "format": the result must be uppercase ASCII letters and digits only, start
       with two letters (the country code) followed by two digits.
    2. "country": the country code must be a key of `lengths`.
    3. "length": the total length must equal lengths[country].
    4. "checksum": move the first four characters to the end, replace every letter by
       a two-digit number (A = 10, B = 11, ..., Z = 35), read the result as one
       integer; it must leave remainder 1 when divided by 97.
    Return "ok" if all checks pass.

    >>> check_iban("GB82 WEST 1234 5698 7654 32", {"GB": 22, "DE": 22})
    'ok'
    >>> check_iban("GB82 WEST 1234 5698 7654 33", {"GB": 22})
    'checksum'
    """
```
