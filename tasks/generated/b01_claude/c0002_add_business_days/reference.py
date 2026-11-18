import datetime as dt
import re

_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _parse(s: str) -> dt.date:
    # fromisoformat alone also accepts forms like "20240308", so check the shape first.
    if not isinstance(s, str) or not _ISO.fullmatch(s):
        raise ValueError(f"bad date: {s!r}")
    return dt.date.fromisoformat(s)


def add_business_days(start: str, n: int, holidays: list[str]) -> str:
    day = _parse(start)
    off = {_parse(h) for h in holidays}

    def is_business(d: dt.date) -> bool:
        return d.weekday() < 5 and d not in off

    if n == 0:
        while not is_business(day):
            day += dt.timedelta(days=1)
        return day.isoformat()
    step = dt.timedelta(days=1 if n > 0 else -1)
    remaining = abs(n)
    while remaining:
        day += step
        if is_business(day):
            remaining -= 1
    return day.isoformat()
