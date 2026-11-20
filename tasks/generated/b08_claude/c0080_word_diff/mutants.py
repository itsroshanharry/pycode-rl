[
    ("insertions win ties", "        elif j == m or (i < n and lcs[i + 1][j] >= lcs[i][j + 1]):", "        elif j == m or (i < n and lcs[i + 1][j] > lcs[i][j + 1]):"),
    ("split on single spaces only", "    x, y = a.split(), b.split()", "    x, y = a.split(\" \"), b.split(\" \")"),
    ("words compared case-insensitively", "            row[j] = below[j + 1] + 1 if x[i] == y[j] else max(below[j], row[j + 1])", "            row[j] = below[j + 1] + 1 if x[i].lower() == y[j].lower() else max(below[j], row[j + 1])"),
]
