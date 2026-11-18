[
    ("a gap of exactly `gap` splits the session", "            if t - prev > gap:", "            if t - prev >= gap:"),
    ("sessions sorted by user before start time", "out.sort(key=lambda s: (s[1], s[0]))", "out.sort(key=lambda s: (s[0], s[1]))"),
    ("duplicate events counted once", "        times.sort()\n", "        times = sorted(set(times))\n"),
]
