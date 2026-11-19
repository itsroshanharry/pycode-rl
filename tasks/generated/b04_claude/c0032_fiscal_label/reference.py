import datetime as dt
import re

_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def fiscal_label(date: str, start_month: int) -> str:
    if not isinstance(date, str) or not _ISO.fullmatch(date):
        raise ValueError(f"bad date: {date!r}")
    d = dt.date.fromisoformat(date)
    if type(start_month) is not int or not 1 <= start_month <= 12:
        raise ValueError("start_month must be an int in 1..12")
    offset = (d.month - start_month) % 12  # months since the fiscal year began
    quarter = offset // 3 + 1
    if start_month == 1:
        year = d.year
    else:
        year = d.year + 1 if d.month >= start_month else d.year
    return f"FY{year}-Q{quarter}"
