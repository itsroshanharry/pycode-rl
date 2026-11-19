[
    ("start treated as 0-based", "        lo = start - 1  # 1-based column -> 0-based index", "        lo = start"),
    ("str fields stripped of all whitespace on both sides", "            value = text.rstrip(\" \")", "            value = text.strip()"),
    ("blank numeric field read as 0", "    if text.strip(\" \") == \"\":\n        return None\n    m = _INT", "    if text.strip(\" \") == \"\":\n        return False, 0\n    m = _INT"),
]
