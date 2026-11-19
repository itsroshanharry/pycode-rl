```python
def income_tax(income: int, allowance: int, taper_threshold: int, bands: list[tuple[int | None, int]]) -> int:
    """Progressive income tax with a personal allowance that tapers away.

    All amounts are whole pence (ints >= 0).
    1. Effective allowance: if income > taper_threshold, the allowance is
       reduced by 1 for every FULL 2 of income above the threshold
       (reduction = (income - taper_threshold) // 2), but not below 0.
    2. Taxable income = max(0, income - effective allowance).
    3. `bands` are (width, rate_percent) applied to taxable income in order:
       the first `width` pence at the first rate, the next band's width at
       its rate, and so on. Only the LAST band has width None (unlimited).
    4. Add up the exact tax of every band and round the TOTAL down to whole
       pence (no rounding per band).

    Raise ValueError if an amount is negative, `bands` is empty, a band
    other than the last has width None or width < 1, the last band's width
    is not None, or a rate is outside 0..100.

    >>> income_tax(5002, 1000, 5000, [(2000, 20), (None, 40)])
    1201
    """
```
