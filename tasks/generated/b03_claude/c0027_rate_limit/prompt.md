```python
def rate_limit(requests: list[tuple[str, int]], window: int, limit: int) -> list[bool]:
    """Decide which requests a per-client sliding-window rate limiter allows.

    Each request is (client, time) with integer times in non-decreasing order. A
    request from client C at time T is allowed if fewer than `limit` of C's
    previously *allowed* requests have a time t with T - window < t <= T;
    otherwise it is denied. Denied requests never count toward the limit, and each
    client is limited independently of the others.
    Return True (allowed) or False (denied) for each request, in order.
    window >= 1 and limit >= 1. There can be up to 30_000 requests; your solution
    must handle that size in well under a second.
    Raise ValueError if window < 1, limit < 1, or a time is smaller than the
    previous request's time.

    >>> rate_limit([("a", 0), ("a", 1), ("a", 2), ("b", 2), ("a", 10)], 10, 2)
    [True, True, False, True, True]
    """
```
