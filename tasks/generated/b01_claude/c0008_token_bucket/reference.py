from fractions import Fraction


def token_bucket(capacity: int, rate: int, requests: list[tuple[int, int]]) -> list[bool]:
    if capacity < 1 or rate < 0:
        raise ValueError("capacity must be >= 1 and rate >= 0")
    tokens = Fraction(capacity)
    last = 0
    out = []
    for t, cost in requests:
        if t < 0 or t < last:
            raise ValueError("request times must be non-negative and non-decreasing")
        if cost < 1:
            raise ValueError("cost must be >= 1")
        tokens = min(Fraction(capacity), tokens + Fraction(rate * (t - last), 1000))
        last = t
        if tokens >= cost:
            tokens -= cost
            out.append(True)
        else:
            out.append(False)
    return out
