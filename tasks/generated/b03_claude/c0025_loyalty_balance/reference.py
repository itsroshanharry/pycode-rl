from collections import deque


def loyalty_balance(events: list[tuple[int, str, int]], expiry_days: int) -> list[int]:
    if expiry_days < 1:
        raise ValueError("expiry_days must be >= 1")
    batches: deque = deque()  # [expires_on_day, remaining], oldest first
    out = []
    last_day = None
    for day, kind, points in events:
        if last_day is not None and day < last_day:
            raise ValueError("days must be non-decreasing")
        if points < 1:
            raise ValueError("points must be >= 1")
        last_day = day
        while batches and batches[0][0] <= day:
            batches.popleft()
        if kind == "earn":
            batches.append([day + expiry_days, points])
        elif kind == "redeem":
            if sum(b[1] for b in batches) >= points:
                need = points
                while need:
                    take = min(need, batches[0][1])
                    batches[0][1] -= take
                    need -= take
                    if batches[0][1] == 0:
                        batches.popleft()
        else:
            raise ValueError(f"unknown kind {kind!r}")
        out.append(sum(b[1] for b in batches))
    return out
