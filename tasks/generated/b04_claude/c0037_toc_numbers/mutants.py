[
    ("equal-level heading treated as a child, not a sibling", "        while stack and stack[-1][0] >= level:", "        while stack and stack[-1][0] > level:"),
    ("sibling counter never advances", '        parent["children"] += 1\n        position = str(parent["children"])', '        position = str(parent["children"] + 1)'),
    ("bool accepted as a level", "        if type(level) is not int or not 1 <= level <= 6:", "        if not isinstance(level, int) or not 1 <= level <= 6:"),
]
