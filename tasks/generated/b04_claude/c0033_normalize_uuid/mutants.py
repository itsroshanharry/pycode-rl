[
    ("hyphens accepted anywhere (removed before checking)", "    for pattern in [*_FORMS, _PLAIN]:\n        m = pattern.fullmatch(text)", "    for pattern in [*_FORMS, _PLAIN]:\n        m = pattern.fullmatch(text if pattern is not _PLAIN else text.replace(\"-\", \"\"))"),
    ("output keeps the input letter case", 'return "-".join(m.groups()).lower()', 'return "-".join(m.groups())'),
    ("urn prefix must be lowercase", 're.compile(r"(?i:urn:uuid:)" + _HYPHENATED),', 're.compile(r"urn:uuid:" + _HYPHENATED),'),
]
