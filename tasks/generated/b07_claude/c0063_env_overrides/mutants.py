[
    ("int conversion checked before bool (bool is an int subclass)", "        if isinstance(current, bool):  # check bool BEFORE int: bool is a subclass of int", "        if isinstance(current, bool) and not isinstance(current, int):"),
    ("prefix matched case-insensitively", "        if not name.startswith(head):", "        if not name.upper().startswith(head.upper()):"),
    ("key parts not lowercased", "        keys = [p.lower() for p in parts]", "        keys = list(parts)"),
]
