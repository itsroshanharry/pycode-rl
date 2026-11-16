[
    ("runs of length 2 are collapsed too", "if j - i + 1 >= 3:", "if j - i + 1 >= 2:"),
    ("duplicates are not removed", "vals = sorted(set(nums))", "vals = sorted(nums)"),
    ("wrong range separator", 'out.append(f"{vals[i]}..{vals[j]}")', 'out.append(f"{vals[i]}-{vals[j]}")'),
]
