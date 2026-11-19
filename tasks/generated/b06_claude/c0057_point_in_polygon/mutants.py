[
    ("edge test excludes the segment's endpoints in y", "and min(y1, y2) <= py <= max(y1, y2):", "and min(y1, y2) < py < max(y1, y2):"),
    ("vertices on the ray counted from both edges (closed interval)", "        if (y1 > py) != (y2 > py):", "        if min(y1, y2) <= py <= max(y1, y2) and y1 != y2:"),
    ("downward edges use the upward comparison", "            else:\n                crosses = lhs > rhs", "            else:\n                crosses = lhs < rhs"),
]
