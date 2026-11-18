[
    ("rotates left instead of right", "rotated = rest[len(rest) - k :] + rest[: len(rest) - k]", "rotated = rest[k:] + rest[:k]"),
    ("matches against the placeholder kept", "            if BYE not in (a, b):\n                matches.append((a, b))", "            matches.append((a, b))"),
    ("duplicate team names accepted", "if len(teams) < 2 or len(set(teams)) != len(teams) or BYE in teams:", "if len(teams) < 2 or BYE in teams:"),
]
