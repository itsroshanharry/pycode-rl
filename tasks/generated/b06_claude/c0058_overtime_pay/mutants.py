[
    ("daily and weekly premiums stack instead of taking the higher", "            halves += max(d, w, s)", "            halves += max(d + w - 2, s)"),
    ("weekly overtime starts at minute 2400 instead of after it", "            w = 3 if week > 2400 else 2", "            w = 3 if week >= 2400 else 2"),
    ("seventh-day rule applied whenever Sunday is worked", "    seventh = all(m > 0 for m in daily_minutes)", "    seventh = daily_minutes[6] > 0"),
]
