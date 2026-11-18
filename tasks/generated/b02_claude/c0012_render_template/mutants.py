[
    ("default used only when missing, not when empty", "out.append(value if value else default)", "out.append(value if value is not None else default)"),
    ("$$ kept as two dollars", "        if nxt == \"$\":\n            out.append(\"$\")", "        if nxt == \"$\":\n            out.append(\"$$\")"),
    ("missing variable silently becomes empty", "            if name not in variables:\n                raise KeyError(name)\n            out.append(variables[name])", "            out.append(variables.get(name, \"\"))"),
]
