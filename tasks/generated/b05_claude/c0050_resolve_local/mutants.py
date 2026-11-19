[
    ("transition instant treated as still in the old period", "            if (k == 0 or starts[k - 1] <= u) and (k == len(starts) or u < starts[k]):", "            if (k == 0 or starts[k - 1] < u) and (k == len(starts) or u <= starts[k]):"),
    ("candidate window misses the last period", "        for k in range(lo, hi + 1):", "        for k in range(lo, hi):"),
    ("offset applied with the wrong sign (local -> UTC adds the offset)", "            u = local - offsets[k]", "            u = local + offsets[k]"),
]
