[
    ("touching ranges not merged", "if merged and lo <= merged[-1][1] + 1:", "if merged and lo <= merged[-1][1]:"),
    ("block alignment ignored when covering a range", "size = lo & -lo if lo else 1 << 32", "size = 1 << 32"),
    ("host bits not cleared", "start = addr & ~(size - 1) & 0xFFFFFFFF", "start = addr"),
]
