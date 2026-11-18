[
    ("extra handicap stroke boundary excluded", "(1 if si <= handicap % n else 0)", "(1 if si < handicap % n else 0)"),
    ("picked-up holes scored as if 0 strokes were played", "        if s == 0:  # picked up\n            continue\n", ""),
    ("negative points not clamped to zero", "total += max(0, 2 + par - net)", "total += 2 + par - net"),
]
