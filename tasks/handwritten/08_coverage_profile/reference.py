def coverage_profile(intervals: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    delta: dict[int, int] = {}
    for start, end, weight in intervals:
        delta[start] = delta.get(start, 0) + weight
        delta[end] = delta.get(end, 0) - weight
    out: list[tuple[int, int, int]] = []
    total, prev = 0, None
    for x in sorted(delta):
        if prev is not None and total != 0:
            if out and out[-1][1] == prev and out[-1][2] == total:
                out[-1] = (out[-1][0], x, total)
            else:
                out.append((prev, x, total))
        total += delta[x]
        prev = x
    return out
