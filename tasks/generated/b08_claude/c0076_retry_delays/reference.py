def retry_delays(base_ms: int, factor: int, cap_ms: int, jitter_pct: list[int], max_attempts: int, budget_ms: int) -> list[int]:
    if base_ms < 1 or factor < 1 or cap_ms < 1 or not 0 <= max_attempts <= 1000 or budget_ms < 0:
        raise ValueError("bad parameters")
    if any(not -50 <= j <= 50 for j in jitter_pct):
        raise ValueError("jitter out of range")
    out, total, current = [], 0, base_ms
    for k in range(max_attempts):
        raw = min(cap_ms, current)  # cap first ...
        j = jitter_pct[k % len(jitter_pct)] if jitter_pct else 0
        delay = raw * (100 + j) // 100  # ... then jitter
        if total + delay > budget_ms:
            break
        out.append(delay)
        total += delay
        if current < cap_ms:
            current *= factor  # stop growing once capped (avoids huge integers)
    return out
