```python
def loyalty_balance(events: list[tuple[int, str, int]], expiry_days: int) -> list[int]:
    """Replay a loyalty-points ledger and report the balance after each event.

    Each event is (day, kind, points) with integer days in non-decreasing order;
    events on the same day are applied in list order. Points are earned in batches:
    an "earn" event adds a batch of `points` that can be used up to and including
    day (earned_day + expiry_days - 1); from day earned_day + expiry_days onward the
    batch's remaining points are gone. A "redeem" event spends `points` taking them
    from the oldest still-valid batches first; if the valid balance is smaller than
    the amount, the redeem is rejected and nothing changes.
    Return, for each event, the total valid balance right after it (counting only
    batches still valid on that event's day).
    Raise ValueError for an unknown kind, points < 1, expiry_days < 1, or a day
    smaller than the previous event's day.

    >>> loyalty_balance([(0, "earn", 100), (5, "earn", 50), (10, "redeem", 120), (30, "earn", 10), (31, "redeem", 20)], 30)
    [100, 150, 30, 40, 20]
    """
```
