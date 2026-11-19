import re
from datetime import date

_DATE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")


def _parse(text: str) -> date:
    m = _DATE.fullmatch(text)
    if not m:
        raise ValueError(f"bad date: {text!r}")
    return date(*map(int, m.groups()))  # ValueError for year 0, Feb 30, ...


def _birthday(b: date, year: int) -> date:
    try:
        return date(year, b.month, b.day)
    except ValueError:
        return date(year, 3, 1)  # Feb 29 birthday in a year without Feb 29


def age_parts(birth: str, on: str) -> tuple[int, int]:
    b, d = _parse(birth), _parse(on)
    if d < b:
        raise ValueError("on is before birth")
    years = d.year - b.year
    if _birthday(b, d.year) > d:
        years -= 1
    last = _birthday(b, b.year + years)
    return years, (d - last).days
