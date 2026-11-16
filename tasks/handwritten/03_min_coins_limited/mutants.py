[
    ("coin counts ignored (unbounded supply)", "        piece = 1\n        while count > 0:", "        count = amount + 1\n        piece = 1\n        while count > 0:"),
    ("duplicate denominations overwrite instead of adding", "counts[value] = counts.get(value, 0) + count", "counts[value] = count"),
    ("off-by-one in the knapsack loop bound", "for a in range(amount, weight - 1, -1):", "for a in range(amount, weight, -1):"),
]
