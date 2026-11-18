[
    ("a single zero group is compressed too", "    if best_len >= 2:", "    if best_len >= 1:"),
    ("rightmost of equal runs is chosen", "            if j - i > best_len:", "            if j - i >= best_len:"),
    ("'::' standing for zero groups is accepted", "        if missing < 1:", "        if missing < 0:"),
]
