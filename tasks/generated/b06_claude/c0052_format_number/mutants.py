[
    ("the first group size repeats instead of the last", "        size = grouping[min(k, len(grouping) - 1)]  # the last size repeats", "        size = grouping[k] if k < len(grouping) else grouping[0]"),
    ("ties rounded half up", "        elif 2 * rem == unit and q % 2:", "        elif 2 * rem == unit:"),
    ("minus sign kept on a value that rounds to zero", "    sign = \"-\" if negative and q else \"\"", "    sign = \"-\" if negative else \"\""),
]
