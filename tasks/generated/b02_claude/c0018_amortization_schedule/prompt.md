```python
def amortization_schedule(principal_cents: int, annual_rate_bp: int, months: int) -> list[tuple[int, int, int]]:
    """Monthly payment schedule of a fixed-rate loan, in integer cents.

    annual_rate_bp is the annual interest rate in basis points (600 means 6%), so
    the monthly rate is r = annual_rate_bp / 120000. The regular payment is
    principal * r / (1 - (1 + r) ** -months), or principal / months if r == 0,
    rounded half-up to a whole cent. Each month: interest = remaining balance * r,
    rounded half-up to a whole cent; principal part = payment - interest; the
    balance drops by the principal part. In the final month, the payment is instead
    whatever clears the loan exactly: principal part = remaining balance and
    payment = remaining balance + interest.
    Return one tuple (payment, interest, principal_part) per month. All
    intermediate values must be computed exactly (no floating point).
    Raise ValueError if principal_cents < 0, annual_rate_bp < 0 or months < 1.

    >>> amortization_schedule(100000, 1200, 3)
    [(34002, 1000, 33002), (34002, 670, 33332), (34003, 337, 33666)]
    >>> amortization_schedule(100, 0, 3)
    [(33, 0, 33), (33, 0, 33), (34, 0, 34)]
    """
```
