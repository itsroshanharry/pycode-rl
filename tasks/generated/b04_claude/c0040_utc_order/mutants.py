[
    ("offset sign reversed (local + offset instead of local - offset)", '        sign = 1 if off[0] == "+" else -1', '        sign = -1 if off[0] == "+" else 1'),
    ("fraction truncated to microseconds", '    digits = frac[1:] if frac else ""', '    digits = frac[1:7] if frac else ""'),
    ("equal instants ordered by string instead of input order", "    order = sorted(range(len(timestamps)), key=lambda i: keys[i])  # stable", "    order = sorted(range(len(timestamps)), key=lambda i: (keys[i], timestamps[i]))"),
]
