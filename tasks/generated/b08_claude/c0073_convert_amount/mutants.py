[
    ("a rate used backwards is not inverted", "        graph.setdefault(b, {})[a] = 1 / Fraction(r)  # rates work backwards too", "        graph.setdefault(b, {})[a] = Fraction(r)  # rates work backwards too"),
    ("neighbours explored in insertion order (ties not lexicographic)", "            for nxt in sorted(graph.get(node, {})):", "            for nxt in graph.get(node, {}):"),
    ("ties rounded half up", "    if rest > Fraction(1, 2) or (rest == Fraction(1, 2) and floor % 2):", "    if rest >= Fraction(1, 2):"),
]
