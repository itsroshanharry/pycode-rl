[
    ("earlier darts counted as ordered (A,B and B,A both counted)", "            for b in _NAMES[i:]:\n                if va + _DARTS[b][0] == rest:\n                    found.add((tuple(sorted((a, b))), final))", "            for b in _NAMES:\n                if va + _DARTS[b][0] == rest:\n                    found.add(((a, b), final))"),
    ("bullseye not accepted as the finishing double", "_DOUBLES = [n for n in _NAMES if n.startswith(\"D\")]", "_DOUBLES = [n for n in _NAMES if n.startswith(\"D\") and n != \"DB\"]"),
    ("equal-value tie-break prefers singles over trebles", "        return (len(earlier), [(-_DARTS[n][0], -_DARTS[n][1]) for n in earlier])", "        return (len(earlier), [(-_DARTS[n][0], _DARTS[n][1]) for n in earlier])"),
]
