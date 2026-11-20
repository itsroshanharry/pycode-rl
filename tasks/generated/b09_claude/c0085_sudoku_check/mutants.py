[
    ("anti-diagonal taken as row + column == 9", "    if r + c == 8:\n        yield \"anti-diagonal\", [(i, 8 - i) for i in range(9)]", "    if r + c == 9:\n        yield \"anti-diagonal\", [(i, 9 - i) for i in range(1, 9)]"),
    ("box start computed from the column index alone", "    br, bc = 3 * (r // 3), 3 * (c // 3)", "    br, bc = 3 * (c // 3), 3 * (c // 3)"),
    ("only the first conflicting unit reported", "            if rules:\n                return r, c, rules", "            if rules:\n                return r, c, rules[:1]"),
]
