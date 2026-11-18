[
    ("week 1 anchored on January 1 instead of January 4", "jan4 = dt.date(year, 1, 4)", "jan4 = dt.date(year, 1, 1)"),
    ("week_start ignored (always Monday)", "(jan4.weekday() - week_start) % 7", "jan4.weekday() % 7"),
    ("late-December dates never move to the next year", "        if d >= nxt:", "        if False:"),
]
