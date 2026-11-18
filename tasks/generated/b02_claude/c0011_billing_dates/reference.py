import calendar
import datetime as dt
import re

_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def billing_dates(anchor: str, count: int) -> list[str]:
    if not isinstance(anchor, str) or not _ISO.fullmatch(anchor):
        raise ValueError(f"bad date: {anchor!r}")
    start = dt.date.fromisoformat(anchor)
    if count < 0:
        raise ValueError("count must be >= 0")
    out = []
    for k in range(count):
        years, month0 = divmod(start.month - 1 + k, 12)
        year, month = start.year + years, month0 + 1
        last = calendar.monthrange(year, month)[1]
        out.append(dt.date(year, month, min(start.day, last)).isoformat())
    return out
