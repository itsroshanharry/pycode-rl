import math
from fractions import Fraction


def _half_up(x: Fraction) -> int:
    return math.floor(x + Fraction(1, 2))


def amortization_schedule(principal_cents: int, annual_rate_bp: int, months: int) -> list[tuple[int, int, int]]:
    if principal_cents < 0 or annual_rate_bp < 0 or months < 1:
        raise ValueError("principal and rate must be >= 0 and months >= 1")
    r = Fraction(annual_rate_bp, 120000)
    if r == 0:
        payment = _half_up(Fraction(principal_cents, months))
    else:
        payment = _half_up(principal_cents * r / (1 - (1 + r) ** -months))
    balance = principal_cents
    schedule = []
    for month in range(1, months + 1):
        interest = _half_up(balance * r)
        if month == months:
            schedule.append((balance + interest, interest, balance))
            balance = 0
        else:
            principal_part = payment - interest
            schedule.append((payment, interest, principal_part))
            balance -= principal_part
    return schedule
