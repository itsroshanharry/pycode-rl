```python
def retry_delays(base_ms: int, factor: int, cap_ms: int, jitter_pct: list[int], max_attempts: int, budget_ms: int) -> list[int]:
    """Delays (ms) before each retry, with exponential backoff, a cap, deterministic jitter and a time budget.

    For retry k = 0, 1, 2, ...:
      raw   = min(cap_ms, base_ms * factor**k)          # the cap applies BEFORE jitter
      j     = jitter_pct[k % len(jitter_pct)], or 0 if jitter_pct is empty
      delay = raw * (100 + j) // 100                     # integer floor division
    So a jittered delay may end up above cap_ms.
    Stop after max_attempts delays, or as soon as the next delay would make
    the running total EXCEED budget_ms (that delay is not included; a total
    exactly equal to the budget is allowed). Return the list of delays.

    Raise ValueError if base_ms < 1, factor < 1, cap_ms < 1, a jitter value is
    outside -50..50, max_attempts < 0 or max_attempts > 1000, or budget_ms < 0.

    >>> retry_delays(100, 2, 1000, [0, 10, -10], 6, 10**9)
    [100, 220, 360, 800, 1100, 900]
    """
```
