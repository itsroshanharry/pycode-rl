from bisect import bisect_left


def reconcile(a: list[tuple[int, int, int]], b: list[tuple[int, int, int]], tol: int):
    if tol < 0:
        raise ValueError("tolerance must be >= 0")
    # Per amount, the unmatched b entries as a sorted list of (day, position in b).
    pools: dict[int, list[tuple[int, int]]] = {}
    for j, (_, day, amount) in enumerate(b):
        pools.setdefault(amount, []).append((day, j))
    for pool in pools.values():
        pool.sort()

    matched_b = [False] * len(b)
    matches, unmatched_a = [], []
    for a_id, day, amount in a:
        pool = pools.get(amount)
        best = None
        if pool:
            p = bisect_left(pool, (day, -1))
            candidates = []
            if p < len(pool):
                candidates.append(p)  # nearest day >= day (lowest position within that day)
            if p > 0:
                prev_day = pool[p - 1][0]
                candidates.append(bisect_left(pool, (prev_day, -1)))  # nearest day < day, lowest position
            for k in candidates:
                d_day, j = pool[k]
                key = (abs(d_day - day), d_day, j)
                if key[0] <= tol and (best is None or key < best[0]):
                    best = (key, k)
        if best is None:
            unmatched_a.append(a_id)
            continue
        _, j = pool.pop(best[1])
        matched_b[j] = True
        matches.append((a_id, b[j][0]))
    unmatched_b = [b[j][0] for j in range(len(b)) if not matched_b[j]]
    return matches, unmatched_a, unmatched_b
