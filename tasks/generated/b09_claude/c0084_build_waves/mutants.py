[
    ("names that only appear as dependencies are not targets (looks like a cycle)", "        for d in ds:\n            graph.setdefault(d, set())  # dependency-only names are targets too\n", ""),
    ("priority ties keep insertion order instead of name order", "        ready.sort(key=lambda t: (-priority.get(t, 0), t))", "        ready.sort(key=lambda t: -priority.get(t, 0))"),
    ("wave listed in priority order instead of by name", "        wave = sorted(ready[:max_parallel])", "        wave = ready[:max_parallel]"),
]
