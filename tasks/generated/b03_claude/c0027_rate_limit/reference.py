from collections import deque


def rate_limit(requests: list[tuple[str, int]], window: int, limit: int) -> list[bool]:
    if window < 1 or limit < 1:
        raise ValueError("window and limit must be >= 1")
    allowed: dict[str, deque] = {}
    out = []
    last = None
    for client, time in requests:
        if last is not None and time < last:
            raise ValueError("times must be non-decreasing")
        last = time
        dq = allowed.setdefault(client, deque())
        while dq and dq[0] <= time - window:  # outside (time - window, time]
            dq.popleft()
        if len(dq) < limit:
            dq.append(time)
            out.append(True)
        else:
            out.append(False)
    return out
