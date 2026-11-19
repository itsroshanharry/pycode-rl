[
    ("country checked before the format", "    if not _SHAPE.fullmatch(s):\n        return \"format\"\n    country = s[:2]\n    if country not in lengths:\n        return \"country\"\n", "    country = s[:2]\n    if country not in lengths:\n        return \"country\"\n    if not _SHAPE.fullmatch(s):\n        return \"format\"\n"),
    ("lowercase letters accepted", 'if not _SHAPE.fullmatch(s):', 'if not _SHAPE.fullmatch(s.upper()):'),
    ("first four characters not moved to the end", "rearranged = s[4:] + s[:4]", "rearranged = s"),
]
