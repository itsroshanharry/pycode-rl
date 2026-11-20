# Naive but correct: walk every day of the range for every worker.
def rota_hours(pattern, offsets, first_day, last_day, holidays):
    if first_day > last_day or not pattern or any(not 0 <= h <= 24 for h in pattern):
        raise ValueError("bad range or pattern")
    hol = set(holidays)
    out = {}
    for worker, k in offsets.items():
        total = 0
        d = first_day
        while d <= last_day:
            h = pattern[(d - k) % len(pattern)]
            p = 2 * min(h, 8) + 3 * max(0, min(h, 12) - 8) + 4 * max(0, h - 12)
            total += 2 * p if d in hol else p
            d += 1
        out[worker] = f"{total // 2}.{5 if total % 2 else 0}"
    return out
