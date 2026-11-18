[
    ("partial comparators padded with zeros instead of compared as a prefix", "    prefix = version[: len(parts)]  # partial comparators look at the first k parts only", "    prefix = version\n    parts = tuple(parts) + (0,) * (3 - len(parts))"),
    ("alternatives combined with AND instead of OR", "if any(all(_holds(pv, op, parts) for op, parts in alt) for alt in alternatives)", "if all(all(_holds(pv, op, parts) for op, parts in alt) for alt in alternatives)"),
    ("a bare version treated as >=", 'comparators.append((m.group(1) or "=", tuple(int(x) for x in m.group(2).split("."))))', 'comparators.append((m.group(1) or ">=", tuple(int(x) for x in m.group(2).split("."))))'),
]
