[
    ("qualified no-cache=\"...\" treated like bare no-cache", '    if any(name == "no-cache" and value is None for name, value in dirs):', '    if any(name == "no-cache" for name, value in dirs):'),
    ("s-maxage also honoured by private caches", '    for directive in (["s-maxage"] if shared else []) + ["max-age"]:', '    for directive in ["s-maxage", "max-age"]:'),
    ("no cap on huge delta-seconds", "            return min(int(values[0]), _CAP)", "            return int(values[0])"),
]
