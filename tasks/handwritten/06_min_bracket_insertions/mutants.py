[
    ("bracket types ignored (one counter)", "def min_bracket_insertions(s: str) -> int:\n", "def min_bracket_insertions(s: str) -> int:\n    bal = need = 0\n    for ch in s:\n        if ch in PAIRS:\n            bal += 1\n        elif bal:\n            bal -= 1\n        else:\n            need += 1\n    return need + bal\n"),
    ("greedy stack instead of interval DP", "def min_bracket_insertions(s: str) -> int:\n", "def min_bracket_insertions(s: str) -> int:\n    stack, need = [], 0\n    for ch in s:\n        if ch in PAIRS:\n            stack.append(ch)\n        elif stack and PAIRS[stack[-1]] == ch:\n            stack.pop()\n        else:\n            need += 1\n    return need + len(stack)\n"),
    ("opening bracket may only be matched, never completed by an insertion", "            best = dp[i + 1][j] + 1  # insert a partner for s[i]\n            c = s[i]\n", "            c = s[i]\n            best = dp[i + 1][j] + 1 if c not in PAIRS else 10**9\n"),
]
