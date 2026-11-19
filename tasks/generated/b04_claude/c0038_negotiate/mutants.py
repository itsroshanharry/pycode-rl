[
    ("specificity ignored: highest q over every matching range", "        quality = by_kind[max(by_kind)] if by_kind else 0", "        quality = max(by_kind.values()) if by_kind else 0"),
    ("ties go to the later offered entry", "        if quality > best_q:", "        if quality and quality >= best_q:"),
    ("offered types matched case-sensitively", '        otype, _, osub = item.lower().partition("/")', '        otype, _, osub = item.partition("/")'),
]
