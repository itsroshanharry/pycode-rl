import re
from datetime import datetime

_TOKEN = r"[!#$%&'*+.^_`|~0-9A-Za-z-]+"
# One list element: optional directive, surrounded by optional spaces/tabs. Always matches.
_ELEMENT = re.compile(rf"[ \t]*(?:({_TOKEN})(?:=({_TOKEN}|\"[^\"\\\\]*\"))?)?[ \t]*")
_DIGITS = re.compile(r"[0-9]+")
_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
_IMF = re.compile(
    rf"({'|'.join(_DAYS)}), ([0-9]{{2}}) ({'|'.join(_MONTHS)}) ([0-9]{{4}}) ([0-9]{{2}}):([0-9]{{2}}):([0-9]{{2}}) GMT"
)
_CAP = 2147483648


def _directives(value: str) -> list[tuple[str, str | None]]:
    """Tokenize with a scanner, not split(','): quoted values may contain commas."""
    out, pos = [], 0
    while True:
        m = _ELEMENT.match(value, pos)
        if m.group(1):
            v = m.group(2)
            out.append((m.group(1).lower(), v[1:-1] if v and v.startswith('"') else v))
        pos = m.end()
        if pos == len(value):
            return out
        if value[pos] != ",":
            raise ValueError(f"malformed Cache-Control at {pos}: {value!r}")
        pos += 1


def _http_date(text: str) -> int | None:
    m = _IMF.fullmatch(text)
    if not m:
        return None
    day, dd, mon, yyyy, hh, mi, ss = m.groups()
    try:
        dt = datetime(int(yyyy), _MONTHS.index(mon) + 1, int(dd), int(hh), int(mi), int(ss))
    except ValueError:
        return None
    if _DAYS[dt.weekday()] != day:
        return None
    return (dt - datetime(1970, 1, 1)).days * 86400 + dt.hour * 3600 + dt.minute * 60 + dt.second


def freshness(headers: dict[str, str], shared: bool) -> int | None:
    h: dict[str, str] = {}
    for name, value in headers.items():
        key = name.lower()
        if key in h:
            raise ValueError(f"duplicate header: {name!r}")
        h[key] = value
    dirs = _directives(h["cache-control"]) if "cache-control" in h else []

    if any(name == "no-cache" and value is None for name, value in dirs):
        return 0
    for directive in (["s-maxage"] if shared else []) + ["max-age"]:
        values = [v for name, v in dirs if name == directive]
        if values:
            if len(values) > 1 or values[0] is None or not _DIGITS.fullmatch(values[0]):
                return 0  # invalid or conflicting lifetime: treat as stale
            return min(int(values[0]), _CAP)
    if "expires" in h:
        expires = _http_date(h["expires"])
        if expires is None:
            return 0
        date = _http_date(h["date"]) if "date" in h else None
        if date is None:
            return None
        return max(0, expires - date)
    return None
