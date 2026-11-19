```python
def rollout_bucket(flag: str, user_id: str, percent: str) -> tuple[int, bool]:
    """Deterministic percentage rollout of a feature flag.

    Hash the UTF-8 BYTES of flag + ":" + user_id with 32-bit FNV-1a:
      h = 0x811C9DC5
      for each byte b: h = h XOR b, then h = (h * 0x01000193) mod 2**32
    The bucket is h mod 10000 (0..9999).

    `percent` is a string: an integer from 0 to 100 written with 1-3 ASCII
    digits (leading zero allowed only as in "05"), optionally followed by "."
    and 1-2 digits ("12.5", "0.01", "100.00"). The value must not exceed 100.
    The user is included iff bucket < percent * 100 (so "0" includes nobody,
    "100" includes everybody, "12.5" includes buckets 0..1249).
    Return (bucket, included). Raise ValueError for a malformed percent or
    one above 100.

    >>> rollout_bucket("new-ui", "user-42", "100")[1]
    True
    """
```
