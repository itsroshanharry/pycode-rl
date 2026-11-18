```python
def token_bucket(capacity: int, rate: int, requests: list[tuple[int, int]]) -> list[bool]:
    """Decide which requests a token-bucket rate limiter accepts.

    The bucket holds at most `capacity` tokens and is full at time 0. Tokens are
    added continuously at `rate` tokens per second (fractions of a token count)
    and never exceed `capacity`. Each request is (time_ms, cost) with time in
    integer milliseconds. A request is accepted if the bucket holds at least `cost`
    tokens at that moment; then `cost` tokens are removed. Otherwise it is rejected
    and nothing is removed. Requests with equal times are handled in list order.
    The arithmetic must be exact (repeated small refills must add up exactly).
    Requires capacity >= 1, rate >= 0 and cost >= 1; raise ValueError if any is out
    of range, or if a time is negative or smaller than the previous request's time.

    >>> token_bucket(2, 1, [(0, 1), (0, 1), (0, 1), (1000, 1)])
    [True, True, False, True]
    >>> token_bucket(5, 2, [(0, 5), (1500, 3), (1600, 1)])
    [True, True, False]
    """
```
