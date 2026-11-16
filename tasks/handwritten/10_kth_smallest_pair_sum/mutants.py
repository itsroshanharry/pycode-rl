[
    ("k treated as 0-indexed", "        if count_at_most(mid) >= k:", "        if count_at_most(mid) >= k + 1:"),
    ("inputs not sorted", "    a, b = sorted(a), sorted(b)\n", ""),
    ("k range not validated", "    if not 1 <= k <= n * m:\n        raise ValueError(\"k out of range\")\n", "    if n * m == 0:\n        raise ValueError(\"k out of range\")\n"),
]
