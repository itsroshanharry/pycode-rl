[
    ("pre-release ranked above the release", "has_no_pre = 0 if pre is not None else 1", "has_no_pre = 1 if pre is not None else 0"),
    ("numeric identifiers compared as text", 'pre_key.append((0, int(ident), ""))', "pre_key.append((1, 0, ident))"),
    ("ties broken by string instead of input order", "key=lambda i: keys[i])", "key=lambda i: (keys[i], versions[i]))"),
]
