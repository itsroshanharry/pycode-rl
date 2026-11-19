import re


def slugify(title: str, translit: dict[str, str], max_len: int) -> str:
    if max_len < 1:
        raise ValueError("max_len must be >= 1")
    s = "".join(translit.get(c, c) for c in title)
    # ASCII-only lowercasing: str.lower() would also turn e.g. the Kelvin sign into "k".
    s = "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)
    words = re.findall(r"[a-z0-9]+", s)
    out = ""
    for w in words:
        candidate = w if not out else out + "-" + w
        if len(candidate) > max_len:
            break
        out = candidate
    if not out and words:
        out = words[0][:max_len]
    return out
