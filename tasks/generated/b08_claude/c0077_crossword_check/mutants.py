[
    ("single letters treated as entries", "    for m in re.finditer(r\"[A-Z]{2,}\", line):", "    for m in re.finditer(r\"[A-Z]+\", line):"),
    ("dictionary compared case-sensitively", "    dictionary = {w.upper() for w in words}", "    dictionary = set(words)"),
    ("all across entries reported before all down entries", "    bad.sort()  # row, col, then \"across\" < \"down\"", "    pass"),
]
