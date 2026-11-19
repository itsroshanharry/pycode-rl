[
    ("translit looked up after lowercasing", "    s = \"\".join(translit.get(c, c) for c in title)", "    s = \"\".join(translit.get(c, c) for c in title.lower())"),
    ("full Unicode lowercasing", "    s = \"\".join(chr(ord(c) + 32) if \"A\" <= c <= \"Z\" else c for c in s)", "    s = s.lower()"),
    ("a slug of exactly max_len is cut further", "        if len(candidate) > max_len:", "        if len(candidate) >= max_len:"),
]
