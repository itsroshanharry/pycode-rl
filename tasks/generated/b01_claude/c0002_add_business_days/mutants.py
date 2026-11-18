[
    ("n == 0 returns start even on a non-business day", "        while not is_business(day):\n            day += dt.timedelta(days=1)\n", ""),
    ("Saturday counted as a business day", "return d.weekday() < 5 and d not in off", "return d.weekday() < 6 and d not in off"),
    ("negative n moves forward", "step = dt.timedelta(days=1 if n > 0 else -1)", "step = dt.timedelta(days=1)"),
]
