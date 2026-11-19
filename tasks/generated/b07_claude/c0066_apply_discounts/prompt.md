```python
def apply_discounts(subtotal: int, coupons: list[dict]) -> tuple[int, list[str]]:
    """Apply coupons to an order subtotal (in cents) and return (total, applied codes).

    Each coupon is a dict with "code" (unique str), "kind" ("percent" or
    "fixed"), "value" (int: percent 1..100, or fixed cents >= 1) and an
    optional "group" (str or None; missing means None).

    1. Exclusivity: within each non-None group only ONE coupon is used: the
       one with the largest nominal discount on the ORIGINAL subtotal
       (percent: subtotal * value / 100, exact; fixed: min(value, subtotal)).
       Ties go to the coupon listed first. Coupons without a group are all used.
    2. All used percent coupons are applied first, in input order, each to the
       RUNNING total: total -= (total * value / 100 rounded to the nearest
       cent, halves up).
    3. Then the used fixed coupons, in input order: total = max(0, total - value).
    Return (final total, codes in the order they were applied).

    Raise ValueError for a negative subtotal, an unknown kind, a value out of
    range, or a duplicate code.

    >>> apply_discounts(10000, [{"code": "F5", "kind": "fixed", "value": 500}, {"code": "P10", "kind": "percent", "value": 10}])
    (8500, ['P10', 'F5'])
    """
```
