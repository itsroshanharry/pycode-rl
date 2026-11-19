[
    ("Feb 29 birthday moved to Feb 28 in non-leap years", "        return date(year, 3, 1)", "        return date(year, 2, 28)"),
    ("a year is only gained the day after the birthday", "    if _birthday(b, d.year) > d:", "    if _birthday(b, d.year) >= d:"),
    ("days counted from this year's birthday even if it has not happened yet", "    last = _birthday(b, b.year + years)", "    last = _birthday(b, d.year)"),
]
