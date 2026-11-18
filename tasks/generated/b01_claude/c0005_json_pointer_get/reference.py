import re

_INDEX = re.compile(r"0|[1-9][0-9]*")


def _decode(token: str) -> str:
    out, i = [], 0
    while i < len(token):
        c = token[i]
        if c == "~":
            nxt = token[i + 1 : i + 2]
            if nxt == "0":
                out.append("~")
            elif nxt == "1":
                out.append("/")
            else:
                raise ValueError(f"invalid escape in token {token!r}")
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def json_pointer_get(doc, pointer: str):
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise ValueError("pointer must be empty or start with '/'")
    tokens = [_decode(t) for t in pointer[1:].split("/")]  # syntax errors first
    cur = doc
    for tok in tokens:
        if isinstance(cur, dict):
            if tok not in cur:
                raise KeyError(tok)
            cur = cur[tok]
        elif isinstance(cur, list):
            if not _INDEX.fullmatch(tok) or int(tok) >= len(cur):
                raise IndexError(tok)
            cur = cur[int(tok)]
        else:
            raise TypeError(f"cannot apply token {tok!r} to a scalar")
    return cur
