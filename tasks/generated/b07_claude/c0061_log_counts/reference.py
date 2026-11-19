import re
from collections import Counter
from datetime import datetime

_LINE = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.[0-9]+)?Z?"
    r" +(\[[A-Za-z]+\]|[A-Za-z]+)(?: (.*))?",
    re.DOTALL,
)
_SEVERITY = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}


def log_counts(lines: list[str]) -> tuple[list[tuple[str, str, int]], int]:
    counts: Counter = Counter()
    malformed = 0
    for raw in lines:
        line = raw[:-2] if raw.endswith("\r\n") else raw[:-1] if raw.endswith("\n") else raw
        if not line.strip():
            continue
        m = _LINE.fullmatch(line)
        if not m:
            malformed += 1
            continue
        y, mo, d, h, mi, s = (int(g) for g in m.groups()[:6])
        try:
            datetime(y, mo, d, h, mi, s)
        except ValueError:
            malformed += 1
            continue
        level = m.group(7).strip("[]").upper()
        if level == "WARNING":
            level = "WARN"
        if level not in _SEVERITY:
            malformed += 1
            continue
        counts[(f"{y:04d}-{mo:02d}-{d:02d}T{h:02d}:{mi:02d}", level)] += 1
    rows = sorted(((minute, lvl, n) for (minute, lvl), n in counts.items()), key=lambda r: (r[0], _SEVERITY[r[1]]))
    return rows, malformed
