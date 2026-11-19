[
    ("each tier's rate applied to everything above its threshold (rates stack)", "        top = x if nxt is None else min(x, nxt)", "        top = x"),
    ("halves rounded down", "    return (num * 2 + 10000) // 20000", "    return (num * 2 + 9999) // 20000"),
    ("each sale's commission rounded separately", "        owed = _round_half_up(_owed_bp(running, tiers))  # round the running total, not each sale\n        out.append(owed - prev)", "        owed = _owed_bp(running, tiers)\n        out.append(_round_half_up(owed - prev) if owed >= prev else -_round_half_up(prev - owed))"),
]
