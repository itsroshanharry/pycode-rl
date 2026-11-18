import datetime as dt
import re

_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def week_label(date: str, week_start: int = 0) -> str:
    if not isinstance(date, str) or not _ISO.fullmatch(date):
        raise ValueError(f"bad date: {date!r}")
    d = dt.date.fromisoformat(date)
    if type(week_start) is not int or not 0 <= week_start <= 6:
        raise ValueError("week_start must be an int from 0 to 6")

    def week1_start(year: int) -> dt.date:
        jan4 = dt.date(year, 1, 4)
        return jan4 - dt.timedelta(days=(jan4.weekday() - week_start) % 7)

    year = d.year
    start = week1_start(year)
    if d < start:
        year -= 1
        start = week1_start(year)
    else:
        nxt = week1_start(year + 1)
        if d >= nxt:
            year += 1
            start = nxt
    week = (d - start).days // 7 + 1
    return f"{year:04d}-W{week:02d}"
