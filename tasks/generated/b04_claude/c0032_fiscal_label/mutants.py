[
    ("fiscal year named after the year it starts", "year = d.year + 1 if d.month >= start_month else d.year", "year = d.year if d.month >= start_month else d.year - 1"),
    ("quarter computed from the calendar month", "quarter = offset // 3 + 1", "quarter = (d.month - 1) // 3 + 1"),
    ("calendar fiscal year (start_month 1) not special-cased", "    if start_month == 1:\n        year = d.year\n    else:\n        year =", "    if False:\n        year = d.year\n    else:\n        year ="),
]
