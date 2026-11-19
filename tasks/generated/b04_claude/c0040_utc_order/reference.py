import re
from datetime import date
from fractions import Fraction

# [0-9], not \d: \d also matches non-ASCII digits such as "٣" or "３".
_RFC3339 = re.compile(
    r"([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]([0-9]{2}):([0-9]{2}):([0-9]{2})"
    r"(\.[0-9]+)?([Zz]|[+-][0-9]{2}:[0-9]{2})"
)


def _instant(ts: str) -> tuple[int, Fraction]:
    m = _RFC3339.fullmatch(ts)
    if not m:
        raise ValueError(f"malformed timestamp: {ts!r}")
    y, mo, d, h, mi, s = (int(g) for g in m.groups()[:6])
    frac, off = m.group(7), m.group(8)
    day = date(y, mo, d)  # ValueError for year 0, month 13, Feb 30, ...
    if h > 23 or mi > 59 or s > 59:
        raise ValueError(f"bad time of day: {ts!r}")
    offset = 0
    if off not in ("Z", "z"):
        oh, om = int(off[1:3]), int(off[4:6])
        if oh > 23 or om > 59:
            raise ValueError(f"bad offset: {ts!r}")
        sign = 1 if off[0] == "+" else -1
        offset = sign * (oh * 3600 + om * 60)
    # Integer seconds (no datetime, so offsets near year 1 or 9999 cannot overflow)
    # plus an exact fraction (no float, no truncation to microseconds).
    seconds = day.toordinal() * 86400 + h * 3600 + mi * 60 + s - offset
    digits = frac[1:] if frac else ""
    return seconds, Fraction(int(digits), 10 ** len(digits)) if digits else Fraction(0)


def utc_order(timestamps: list[str]) -> list[str]:
    keys = [_instant(t) for t in timestamps]  # validate everything first
    order = sorted(range(len(timestamps)), key=lambda i: keys[i])  # stable
    return [timestamps[i] for i in order]
