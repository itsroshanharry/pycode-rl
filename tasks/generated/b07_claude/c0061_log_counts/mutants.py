[
    ("WARNING not folded into WARN (rejected as unknown)", "        if level == \"WARNING\":\n            level = \"WARN\"\n", ""),
    ("unbalanced brackets accepted", "    r\" +(\\[[A-Za-z]+\\]|[A-Za-z]+)(?: (.*))?\",", "    r\" +(\\[?[A-Za-z]+\\]?)(?: (.*))?\","),
    ("levels within a minute sorted alphabetically", "key=lambda r: (r[0], _SEVERITY[r[1]]))", "key=lambda r: (r[0], r[1]))"),
]
