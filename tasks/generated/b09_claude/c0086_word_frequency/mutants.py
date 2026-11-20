[
    ("connectors allowed anywhere in a word (leading/trailing/doubled)", "_WORD = re.compile(r\"[A-Za-z]+(?:['-][A-Za-z]+)*\")", "_WORD = re.compile(r\"[A-Za-z]+(?:['-]+[A-Za-z]*)*\")"),
    ("connectors counted toward min_letters", "        if sum(c.isalpha() for c in word) < min_letters:  # connectors are not letters", "        if len(word) < min_letters:"),
    ("stop words compared without lowercasing them", "    stops = {_lower_ascii(w) for w in stop_words}", "    stops = set(stop_words)"),
]
