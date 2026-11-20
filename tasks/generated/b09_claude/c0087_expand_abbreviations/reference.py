import re

_TOKEN = re.compile(r"[A-Za-z.]+")


def _lower(s: str) -> str:
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s)


def _cased(matched: str, expansion: str) -> str:
    letters = [c for c in matched if c.isascii() and c.isalpha()]
    if len(letters) >= 2 and all("A" <= c <= "Z" for c in letters):
        return expansion.upper()
    if letters and "A" <= letters[0] <= "Z":
        return expansion[:1].upper() + expansion[1:]
    return expansion


def expand_abbreviations(text: str, abbrevs: dict[str, str]) -> str:
    table = {_lower(k): v for k, v in abbrevs.items()}

    def replace(m: re.Match) -> str:
        token = m.group()
        if _lower(token) in table:  # rule 1: the whole token
            return _cased(token, table[_lower(token)])
        if token.endswith(".") and _lower(token[:-1]) in table:  # rule 2: keep the sentence period
            return _cased(token[:-1], table[_lower(token[:-1])]) + "."
        return token

    return _TOKEN.sub(replace, text)
