[
    ("export prefix not recognised", '_LINE = re.compile(r"\\s*(?:export +)?([A-Za-z_][A-Za-z0-9_]*) *= *(.*)", re.DOTALL)', '_LINE = re.compile(r"\\s*([A-Za-z_][A-Za-z0-9_]*) *= *(.*)", re.DOTALL)'),
    ("escapes decoded inside single quotes too", "        if c == \"\\\\\" and quote == '\"':", "        if c == \"\\\\\":"),
    ("any '#' starts a comment in an unquoted value", '            cut = rest.find(" #")', '            cut = rest.find("#")'),
]
