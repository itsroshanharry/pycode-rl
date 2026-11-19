def elevator_scan(start: int, direction: str, requests: list[int], top: int) -> tuple[list[int], int]:
    if direction not in ("up", "down") or top < 0:
        raise ValueError("bad direction or top")
    if any(not 0 <= f <= top for f in [start, *requests]):
        raise ValueError("floor out of range")
    pending = set(requests)
    order: list[int] = []
    if start in pending:
        order.append(start)
        pending.discard(start)
    if direction == "up":
        ahead = sorted(f for f in pending if f > start)
        behind = sorted((f for f in pending if f < start), reverse=True)  # nearest first after reversing
        end = top
    else:
        ahead = sorted((f for f in pending if f < start), reverse=True)
        behind = sorted(f for f in pending if f > start)
        end = 0
    order += ahead
    if behind:
        # SCAN: run to the end floor before reversing, even with nothing ahead.
        distance = abs(end - start) + abs(end - behind[-1])
        order += behind
    elif ahead:
        distance = abs(ahead[-1] - start)
    else:
        distance = 0
    return order, distance
