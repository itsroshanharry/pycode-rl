[
    ("equal scores ranked by name descending", "key=lambda m: (-m[1], m[0]))", "key=lambda m: (-m[1], tuple(-ord(c) for c in m[0])))"),
    ("lowest scores first", "key=lambda m: (-m[1], m[0]))", "key=lambda m: (m[1], m[0]))"),
    ("one row too many per group", "out[group] = [name for name, _ in ranked[:k]]", "out[group] = [name for name, _ in ranked[: k + 1]]"),
]
