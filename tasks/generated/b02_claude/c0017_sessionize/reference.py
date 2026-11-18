def sessionize(events: list[tuple[str, int]], gap: int) -> list[tuple[str, int, int, int]]:
    if gap < 0:
        raise ValueError("gap must be >= 0")
    by_user: dict[str, list[int]] = {}
    for user, t in events:
        by_user.setdefault(user, []).append(t)
    out = []
    for user, times in by_user.items():
        times.sort()
        start = prev = times[0]
        count = 0
        for t in times:
            if t - prev > gap:
                out.append((user, start, prev, count))
                start, count = t, 0
            count += 1
            prev = t
        out.append((user, start, prev, count))
    out.sort(key=lambda s: (s[1], s[0]))
    return out
