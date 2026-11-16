[
    ("adjacent equal segments are not merged", "            if out and out[-1][1] == prev and out[-1][2] == total:", "            if False:"),
    ("zero-total gaps are emitted as segments", "        if prev is not None and total != 0:", "        if prev is not None:"),
    ("intervals treated as closed [start, end]", "        delta[end] = delta.get(end, 0) - weight", "        delta[end + 1] = delta.get(end + 1, 0) - weight"),
]
