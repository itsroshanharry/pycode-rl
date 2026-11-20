```python
def proration_credit(cycle_start: str, cycle_end: str, change_date: str, old_price: int, new_price: int) -> int:
    """Amount (cents) to charge now when a subscription changes plan mid-cycle.

    Dates are "YYYY-MM-DD" (ASCII digits, real dates). The billing cycle
    covers the days from cycle_start up to but NOT including cycle_end. The
    plan changes at the start of change_date, so change_date itself is billed
    at the new price. Prices are per whole cycle, in cents (>= 0).

      total_days = days from cycle_start to cycle_end
      remaining  = days from change_date to cycle_end
      amount     = (new_price - old_price) * remaining / total_days

    Round exactly to whole cents with halves rounded AWAY FROM ZERO. A
    downgrade gives a negative amount (a credit).
    Raise ValueError for malformed dates, cycle_start >= cycle_end, a
    change_date outside [cycle_start, cycle_end), or a negative price.

    >>> proration_credit("2024-01-01", "2024-02-01", "2024-01-16", 1000, 2000)
    516
    >>> proration_credit("2024-01-01", "2024-02-01", "2024-01-16", 2000, 1000)
    -516
    """
```
