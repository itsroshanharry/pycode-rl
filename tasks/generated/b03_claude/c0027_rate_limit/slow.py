# Correct but naive: rescan the full history of allowed requests every time (O(n^2)).
def rate_limit(requests: list[tuple[str, int]], window: int, limit: int) -> list[bool]:
    if window < 1 or limit < 1:
        raise ValueError("window and limit must be >= 1")
    history = []
    out = []
    last = None
    for client, time in requests:
        if last is not None and time < last:
            raise ValueError("times must be non-decreasing")
        last = time
        recent = sum(1 for c, t in history if c == client and time - window < t <= time)
        ok = recent < limit
        if ok:
            history.append((client, time))
        out.append(ok)
    return out
