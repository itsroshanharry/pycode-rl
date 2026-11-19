```python
def invoice_tax_diff(lines: list[int], rate_bp: int) -> tuple[int, int, int]:
    """Compare per-line and per-invoice tax rounding.

    `lines` are net amounts in cents (negative = credit line); `rate_bp` is the
    tax rate in basis points (1 bp = 0.01%), rate_bp >= 0.
    Rounding is to the nearest cent with halves rounded AWAY FROM ZERO
    (0.5 -> 1, -0.5 -> -1, -1.5 -> -2), computed exactly (no floats).
    - per_line = the sum over lines of round(line * rate_bp / 10000);
    - per_invoice = round(sum(lines) * rate_bp / 10000).
    Return (per_line, per_invoice, per_line - per_invoice).
    Raise ValueError if rate_bp < 0.

    >>> invoice_tax_diff([5, 5, 5], 1000)
    (3, 2, 1)
    """
```
