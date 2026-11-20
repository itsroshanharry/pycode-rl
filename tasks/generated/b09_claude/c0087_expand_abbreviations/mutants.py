[
    ("no sentence-period rule (approx. is left alone)", "        if token.endswith(\".\") and _lower(token[:-1]) in table:  # rule 2: keep the sentence period\n            return _cased(token[:-1], table[_lower(token[:-1])]) + \".\"\n", ""),
    ("a single uppercase letter counts as all-caps", "    if len(letters) >= 2 and all(\"A\" <= c <= \"Z\" for c in letters):", "    if letters and all(\"A\" <= c <= \"Z\" for c in letters):"),
    ("keys compared case-sensitively", "    table = {_lower(k): v for k, v in abbrevs.items()}", "    table = dict(abbrevs)"),
]
