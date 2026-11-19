# Naive but correct: test every minute up to 9999-12-31T23:59.
# Billions of iterations when the next match is far away or never comes.
import re
from datetime import datetime, timedelta

_BOUNDS = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
_ITEM = re.compile(r"(?:(\*)|([0-9]+)(?:-([0-9]+))?)(?:/([0-9]+))?")
_STAMP = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2})")


def _field(text, lo, hi):
    values = set()
    for item in text.split(","):
        m = _ITEM.fullmatch(item)
        if not m:
            raise ValueError(item)
        star, a, b, step = m.groups()
        if star:
            start, end = lo, hi
        else:
            start = int(a)
            end = int(b) if b is not None else (hi if step is not None else start)
        stride = int(step) if step is not None else 1
        if not (lo <= start <= hi and lo <= end <= hi) or start > end or stride < 1:
            raise ValueError(item)
        values.update(range(start, end + 1, stride))
    return values


def cron_next(expr, after):
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError("expected 5 fields")
    minutes, hours, doms, months, dows = (_field(f, lo, hi) for f, (lo, hi) in zip(fields, _BOUNDS))
    dom_any, dow_any = fields[2] == "*", fields[4] == "*"
    m = _STAMP.fullmatch(after)
    if not m:
        raise ValueError(after)
    t = datetime(*map(int, m.groups()))
    end = datetime(9999, 12, 31, 23, 59)
    step = timedelta(minutes=1)
    while t < end:
        t += step
        if t.minute in minutes and t.hour in hours and t.month in months:
            dom_ok = t.day in doms
            dow_ok = t.isoweekday() % 7 in dows
            if (dom_ok or dow_ok) if not dom_any and not dow_any else (dom_ok and dow_ok):
                return f"{t.year:04d}-{t.month:02d}-{t.day:02d}T{t.hour:02d}:{t.minute:02d}"
    return None
