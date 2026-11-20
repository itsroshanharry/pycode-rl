def word_diff(a: str, b: str) -> list[tuple[str, str]]:
    x, y = a.split(), b.split()
    n, m = len(x), len(y)
    # lcs[i][j] = LCS length of x[i:] and y[j:] (suffix table, so the walk can go forwards)
    lcs = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        row, below = lcs[i], lcs[i + 1]
        for j in range(m - 1, -1, -1):
            row[j] = below[j + 1] + 1 if x[i] == y[j] else max(below[j], row[j + 1])
    ops, i, j = [], 0, 0
    while i < n or j < m:
        if i < n and j < m and x[i] == y[j]:
            ops.append(("=", x[i]))
            i += 1
            j += 1
        elif j == m or (i < n and lcs[i + 1][j] >= lcs[i][j + 1]):
            ops.append(("-", x[i]))  # deletions win ties
            i += 1
        else:
            ops.append(("+", y[j]))
            j += 1
    return ops
