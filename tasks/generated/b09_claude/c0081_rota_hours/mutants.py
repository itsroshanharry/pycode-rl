[
    ("offset added instead of subtracted (worker position (d + k) % L)", "            total += value[(d - k) % L]\n        for d in in_range:", "            total += value[(d + k) % L]\n        for d in in_range:"),
    ("holiday doubles the hours worked before the overtime tiers (paid(2h) instead of 2*paid(h))", "            total += value[(d - k) % L]  # doubling = add the day's value once more", "            total += _paid_halves(2 * pattern[(d - k) % L]) - value[(d - k) % L]"),
    ("duplicate holidays counted more than once", "    in_range = sorted({h for h in holidays if first_day <= h <= last_day})  # duplicates count once", "    in_range = sorted(h for h in holidays if first_day <= h <= last_day)"),
]
