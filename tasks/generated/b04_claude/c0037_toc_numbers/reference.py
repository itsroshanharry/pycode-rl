def toc_numbers(headings: list[tuple[int, str]]) -> list[str]:
    root = {"number": "", "children": 0}
    stack: list[tuple[int, dict]] = []  # chain of ancestors of the previous heading
    out = []
    for level, title in headings:
        if type(level) is not int or not 1 <= level <= 6:
            raise ValueError(f"bad heading level: {level!r}")
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else root
        parent["children"] += 1
        position = str(parent["children"])
        number = f"{parent['number']}.{position}" if parent["number"] else position
        node = {"number": number, "children": 0}
        stack.append((level, node))
        out.append(f"{number} {title}")
    return out
