def _paid_halves(h: int) -> int:
    """Paid hours for one day, in half hours (exact): 1x to 8, 1.5x to 12, 2x above."""
    return 2 * min(h, 8) + 3 * max(0, min(h, 12) - 8) + 4 * max(0, h - 12)


def rota_hours(pattern: list[int], offsets: dict[str, int], first_day: int, last_day: int,
               holidays: list[int]) -> dict[str, str]:
    if first_day > last_day or not pattern or any(not 0 <= h <= 24 for h in pattern):
        raise ValueError("bad range or pattern")
    L = len(pattern)
    value = [_paid_halves(h) for h in pattern]
    cycle_total = sum(value)
    days = last_day - first_day + 1
    full, rest = divmod(days, L)
    in_range = sorted({h for h in holidays if first_day <= h <= last_day})  # duplicates count once
    out = {}
    for worker, k in offsets.items():
        total = full * cycle_total  # whole cycles, O(1) instead of one step per day
        start = first_day + full * L
        for d in range(start, start + rest):  # the partial cycle at the end (< L days)
            total += value[(d - k) % L]
        for d in in_range:
            total += value[(d - k) % L]  # doubling = add the day's value once more
        out[worker] = f"{total // 2}.{5 if total % 2 else 0}"
    return out
