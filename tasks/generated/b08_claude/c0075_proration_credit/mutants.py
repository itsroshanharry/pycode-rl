[
    ("change day billed at the old price", "    remaining = (end - change).days  # the change day itself is billed at the new price", "    remaining = (end - change).days - 1"),
    ("cycle end treated as inclusive", "    total_days = (end - start).days  # end is exclusive", "    total_days = (end - start).days + 1"),
    ("halves rounded up toward +infinity", "    q = (2 * abs(num) + den) // (2 * den)  # halves away from zero\n    return q if num >= 0 else -q", "    return (2 * num + den) // (2 * den)"),
]
