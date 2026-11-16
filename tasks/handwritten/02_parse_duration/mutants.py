[
    ("units accepted in any order", "        if idx <= last:\n            raise ValueError(\"repeated or out-of-order unit\")\n", "        if idx == last:\n            raise ValueError(\"repeated or out-of-order unit\")\n"),
    ("spaces stripped everywhere, so '1 h' is accepted", '    s = text.strip(" ")', '    s = text.replace(" ", "")'),
    ("empty text returns 0 instead of raising", '    s = text.strip(" ")\n', '    s = text.strip(" ")\n    if not s:\n        return 0\n'),
]
