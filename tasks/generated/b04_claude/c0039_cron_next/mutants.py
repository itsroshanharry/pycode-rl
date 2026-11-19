[
    ("day fields always ANDed (ignores the either-matches rule)", "        ok = (dom_ok or dow_ok) if not dom_any and not dow_any else (dom_ok and dow_ok)", "        ok = dom_ok and dow_ok"),
    ("a field starting with '*' (e.g. '*/2') counted as unrestricted", '    dom_any, dow_any = fields[2] == "*", fields[4] == "*"', '    dom_any, dow_any = fields[2].startswith("*"), fields[4].startswith("*")'),
    ("weekday numbered from Monday = 0", "    first = date(year, month, 1).isoweekday() % 7  # weekday of the 1st, Sunday = 0", "    first = date(year, month, 1).weekday()"),
]
