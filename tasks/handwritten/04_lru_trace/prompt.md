```python
def lru_trace(capacity: int, ops: list[tuple]) -> list[int]:
    """Simulate a least-recently-used (LRU) cache and return the results of reads.

    Each op is either ("put", key, value) or ("get", key), with integer keys and
    values. "put" stores the value under key, overwriting any previous value.
    "get" returns the stored value, or -1 if the key is absent. A successful "get"
    and every "put" make that key the most recently used one; a failed "get"
    changes nothing. When a "put" inserts a new key while the cache already holds
    `capacity` keys, the least recently used key is evicted first. With capacity 0
    nothing is ever stored.
    Return the list of "get" results in order.

    >>> lru_trace(2, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("get", 3)])
    [1, -1, 3]
    """
```
