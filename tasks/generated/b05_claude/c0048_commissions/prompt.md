```python
def commissions(sales: list[int], tiers: list[tuple[int, int]]) -> list[int]:
    """Commission in cents for each sale of a period, using marginal tiers.

    `sales` are amounts in cents in time order (a negative amount is a refund).
    `tiers` is a list of (threshold, rate) with thresholds in cents, strictly
    increasing and starting at 0, and rates in basis points (1 bp = 0.01%).
    A tier's rate applies to the part of the period's RUNNING TOTAL that lies
    at or above its threshold and below the next tier's threshold.

    Let C(x) be the exact commission owed on a running total x (C(x) = 0 when
    x <= 0), and R(x) be C(x) rounded to whole cents, with halves rounded up.
    Let total_i be the running total after sale i, and total_before = 0 for
    the first sale. The commission for sale i is R(total_i) - R(total_(i-1)).
    So the per-sale commissions always add up to the rounded commission on the
    period total, and a refund can give a negative commission.

    Raise ValueError if `tiers` is empty, the first threshold is not 0, the
    thresholds are not strictly increasing, or a rate is negative.

    >>> commissions([100000, 50000], [(0, 500), (120000, 1000)])
    [5000, 4000]
    >>> commissions([1, 1, 1], [(0, 5000)])
    [1, 0, 1]
    """
```
