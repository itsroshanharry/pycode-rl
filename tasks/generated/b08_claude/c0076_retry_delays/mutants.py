[
    ("jitter applied before the cap", "        delay = raw * (100 + j) // 100  # ... then jitter", "        delay = min(cap_ms, current * (100 + j) // 100)"),
    ("a total exactly equal to the budget is rejected", "        if total + delay > budget_ms:", "        if total + delay >= budget_ms:"),
    ("jitter sequence starts at its second entry", "        j = jitter_pct[k % len(jitter_pct)] if jitter_pct else 0", "        j = jitter_pct[(k + 1) % len(jitter_pct)] if jitter_pct else 0"),
]
