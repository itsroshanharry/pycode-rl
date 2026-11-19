import calendar
import re
from datetime import date, datetime, timedelta

_BOUNDS = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
_ITEM = re.compile(r"(?:(\*)|([0-9]+)(?:-([0-9]+))?)(?:/([0-9]+))?")
_STAMP = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2})")


def _field(text: str, lo: int, hi: int) -> set[int]:
    values: set[int] = set()
    for item in text.split(","):
        m = _ITEM.fullmatch(item)
        if not m:
            raise ValueError(f"bad cron item: {item!r}")
        star, a, b, step = m.groups()
        if star:
            start, end = lo, hi
        else:
            start = int(a)
            end = int(b) if b is not None else (hi if step is not None else start)
        stride = int(step) if step is not None else 1
        if not (lo <= start <= hi and lo <= end <= hi) or start > end or stride < 1:
            raise ValueError(f"bad cron item: {item!r}")
        values.update(range(start, end + 1, stride))
    return values


def _matching_days(year, month, doms, dows, dom_any, dow_any) -> list[int]:
    dim = calendar.monthrange(year, month)[1]
    if dow_any:  # only the day-of-month field constrains: list those days directly
        return [d for d in sorted(doms) if d <= dim]
    first = date(year, month, 1).isoweekday() % 7  # weekday of the 1st, Sunday = 0
    days = []
    for d in range(1, dim + 1):
        dom_ok = d in doms
        dow_ok = (first + d - 1) % 7 in dows
        ok = (dom_ok or dow_ok) if not dom_any and not dow_any else (dom_ok and dow_ok)
        if ok:
            days.append(d)
    return days


def cron_next(expr: str, after: str) -> str | None:
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError("expected 5 fields")
    minutes, hours, doms, months, dows = (_field(f, lo, hi) for f, (lo, hi) in zip(fields, _BOUNDS))
    minutes, hours = sorted(minutes), sorted(hours)
    dom_any, dow_any = fields[2] == "*", fields[4] == "*"

    m = _STAMP.fullmatch(after)
    if not m:
        raise ValueError(f"bad timestamp: {after!r}")
    base = datetime(*map(int, m.groups()))  # raises ValueError for impossible dates/times
    if base == datetime(9999, 12, 31, 23, 59):
        return None
    start = base + timedelta(minutes=1)  # strictly after
    start_key = (start.year, start.month, start.day)

    # Walk months, not minutes or days: ~96k cheap iterations even when nothing ever matches.
    year, month = start.year, start.month
    while year <= 9999:
        if month in months:
            for d in _matching_days(year, month, doms, dows, dom_any, dow_any):
                if (year, month, d) < start_key:
                    continue
                first_day = (year, month, d) == start_key
                for h in hours:
                    if first_day and h < start.hour:
                        continue
                    for mi in minutes:
                        if first_day and h == start.hour and mi < start.minute:
                            continue
                        return f"{year:04d}-{month:02d}-{d:02d}T{h:02d}:{mi:02d}"
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return None
