def _owed_bp(x: int, tiers: list[tuple[int, int]]) -> int:
    """C(x) * 10000, exact integer (cents x basis points)."""
    if x <= 0:
        return 0
    num = 0
    for k, (threshold, rate) in enumerate(tiers):
        if x <= threshold:
            break
        nxt = tiers[k + 1][0] if k + 1 < len(tiers) else None
        top = x if nxt is None else min(x, nxt)
        num += (top - threshold) * rate
    return num


def _round_half_up(num: int) -> int:
    """num / 10000 rounded to the nearest integer, halves up (num >= 0)."""
    return (num * 2 + 10000) // 20000


def commissions(sales: list[int], tiers: list[tuple[int, int]]) -> list[int]:
    if not tiers or tiers[0][0] != 0:
        raise ValueError("tiers must start at threshold 0")
    for (a, _), (b, _) in zip(tiers, tiers[1:]):
        if b <= a:
            raise ValueError("thresholds must be strictly increasing")
    if any(rate < 0 for _, rate in tiers):
        raise ValueError("negative rate")
    out, running, prev = [], 0, 0
    for amount in sales:
        running += amount
        owed = _round_half_up(_owed_bp(running, tiers))  # round the running total, not each sale
        out.append(owed - prev)
        prev = owed
    return out
