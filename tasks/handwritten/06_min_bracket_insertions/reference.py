PAIRS = {"(": ")", "[": "]", "{": "}"}


def min_bracket_insertions(s: str) -> int:
    n = len(s)
    # dp[i][j]: answer for the substring s[i:j].
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    for length in range(1, n + 1):
        for i in range(n - length + 1):
            j = i + length
            best = dp[i + 1][j] + 1  # insert a partner for s[i]
            c = s[i]
            if c in PAIRS:
                for k in range(i + 1, j):
                    if s[k] == PAIRS[c]:  # match s[i] with s[k]
                        cand = dp[i + 1][k] + dp[k + 1][j]
                        if cand < best:
                            best = cand
            dp[i][j] = best
    return dp[0][n]
