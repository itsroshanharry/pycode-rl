[
    ("count only includes rows with a value", "        s[0] += 1  # every row counts\n        v = row.get(value)\n        if v is not None:\n", "        v = row.get(value)\n        if v is not None:\n            s[0] += 1\n"),
    ("None sorted after other values", "    return tuple((0,) if x is None else (1, x) for x in group)", "    return tuple((2,) if x is None else (1, x) for x in group)"),
    ("min/max default to 0 when a group has no values", "        s = stats.setdefault(group, [0, 0, None, None])", "        s = stats.setdefault(group, [0, 0, 0, 0])"),
]
