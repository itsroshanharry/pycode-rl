[
    ("sign bit threshold off by one (most negative value read as positive)", "        if signed and raw >= 1 << (width - 1):", "        if signed and raw > 1 << (width - 1):"),
    ("duplicate check uses the raw name, so 'a' and 'a!' collide silently", "        seen.add(key)", "        seen.add(name)"),
    ("stray-bit check only looks above the highest field (misses gaps)", "    if value & ~covered:", "    if value >> prev_end:"),
]
