def wrap_text(text: str, width: int) -> list[str]:
    words = []
    for word in text.split():
        for i in range(0, len(word), width):
            words.append(word[i : i + width])
    lines: list[str] = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
