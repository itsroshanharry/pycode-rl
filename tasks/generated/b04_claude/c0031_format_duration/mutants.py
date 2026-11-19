[
    ("truncates instead of rounding half up", "rounded = (value + step // 2) // step * step", "rounded = value // step * step"),
    ("zero-valued units are written out", "        if count:\n            parts.append(f\"{count}{name}\")", "        parts.append(f\"{count}{name}\")"),
    ("carry into a larger unit not re-normalized", "            value = rounded  # carried into the next larger unit: start again\n            continue", "            pass"),
]
