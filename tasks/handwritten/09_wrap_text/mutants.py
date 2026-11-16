[
    ("off-by-one: a line of exactly `width` characters is split", "elif len(current) + 1 + len(word) <= width:", "elif len(current) + 1 + len(word) < width:"),
    ("long words are not split", "        for i in range(0, len(word), width):\n            words.append(word[i : i + width])", "        words.append(word)"),
    ("splits on single spaces only, keeping newlines and empty words", "    for word in text.split():", "    for word in text.split(\" \"):"),
]
