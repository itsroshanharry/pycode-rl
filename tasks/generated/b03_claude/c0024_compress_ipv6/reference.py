import re

_GROUP = re.compile(r"[0-9A-Fa-f]{1,4}")


def _groups(part: str) -> list[str]:
    if part == "":
        return []
    groups = part.split(":")
    if not all(_GROUP.fullmatch(g) for g in groups):
        raise ValueError("malformed group")
    return groups


def compress_ipv6(addr: str) -> str:
    if addr.count("::") > 1:
        raise ValueError("more than one '::'")
    if "::" in addr:
        left, right = addr.split("::")
        head, tail = _groups(left), _groups(right)
        missing = 8 - len(head) - len(tail)
        if missing < 1:
            raise ValueError("'::' must stand for at least one zero group")
        groups = head + ["0"] * missing + tail
    else:
        groups = _groups(addr)
        if len(groups) != 8:
            raise ValueError("need exactly 8 groups")
    values = [int(g, 16) for g in groups]
    best_start, best_len, i = -1, 0, 0
    while i < 8:  # find the longest (leftmost on ties) run of zero groups
        if values[i] == 0:
            j = i
            while j < 8 and values[j] == 0:
                j += 1
            if j - i > best_len:
                best_start, best_len = i, j - i
            i = j
        else:
            i += 1
    text = [format(v, "x") for v in values]
    if best_len >= 2:
        left = ":".join(text[:best_start])
        right = ":".join(text[best_start + best_len :])
        return f"{left}::{right}"
    return ":".join(text)
