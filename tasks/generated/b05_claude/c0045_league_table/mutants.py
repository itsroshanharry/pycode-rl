[
    ("head-to-head table uses every match of a group member, not only matches between members", "if m[0] in members and m[3] in members", "if m[0] in members or m[3] in members"),
    ("head-to-head skipped: tied teams ordered by name", "            group = sorted(group, key=lambda t: (-h2h[t][0], -h2h[t][1], -h2h[t][2], t))", "            group = sorted(group)"),
    ("goals scored not used as an overall tie-breaker (goes straight to head-to-head)", "        groups.setdefault(tuple(overall[t]), []).append(t)", "        groups.setdefault(tuple(overall[t][:2]), []).append(t)"),
]
