[
    ("equal distances resolved toward the later day", "                key = (abs(d_day - day), d_day, j)", "                key = (abs(d_day - day), -d_day, j)"),
    ("only entries on or after the day are considered", "            if p > 0:\n                prev_day = pool[p - 1][0]\n                candidates.append(bisect_left(pool, (prev_day, -1)))  # nearest day < day, lowest position\n", ""),
    ("among equal earlier days the last entry of b is taken", "                candidates.append(bisect_left(pool, (prev_day, -1)))  # nearest day < day, lowest position", "                candidates.append(p - 1)"),
]
