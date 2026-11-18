[
    ("always clamps to the 28th", "min(start.day, last)", "min(start.day, 28)"),
    ("month offset off by one", "divmod(start.month - 1 + k, 12)", "divmod(start.month + k, 12)"),
    ("negative count returns [] instead of raising", "    if count < 0:\n", "    if count < -1:\n"),
]
