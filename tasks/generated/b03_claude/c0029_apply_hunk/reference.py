import re

_HEADER = re.compile(r"@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@.*", re.DOTALL)


def apply_hunk(lines: list[str], hunk: list[str]) -> list[str]:
    if not hunk:
        raise ValueError("empty hunk")
    m = _HEADER.fullmatch(hunk[0])
    if not m:
        raise ValueError(f"malformed header: {hunk[0]!r}")
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) is not None else 1
    d = int(m.group(4)) if m.group(4) is not None else 1
    old, new = [], []
    for entry in hunk[1:]:
        tag, text = entry[:1], entry[1:]
        if tag == " ":
            old.append(text)
            new.append(text)
        elif tag == "-":
            old.append(text)
        elif tag == "+":
            new.append(text)
        else:
            raise ValueError(f"bad hunk line: {entry!r}")
    if len(old) != b or len(new) != d:
        raise ValueError("line counts do not match the header")
    start = a - 1 if b > 0 else a  # B == 0: insert after line A
    if start < 0 or lines[start : start + b] != old:
        raise ValueError("hunk does not apply at the stated position")
    return lines[:start] + new + lines[start + b :]
