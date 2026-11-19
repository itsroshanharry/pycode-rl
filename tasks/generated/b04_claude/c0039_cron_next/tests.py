import random
from datetime import datetime, timedelta

import pytest
from solution import cron_next


@pytest.mark.parametrize(
    "expr, after, expected",
    [
        ("*/15 * * * *", "2024-05-01T10:07", "2024-05-01T10:15"),
        ("*/15 * * * *", "2024-05-01T10:15", "2024-05-01T10:30"),
        ("* * * * *", "2024-12-31T23:59", "2025-01-01T00:00"),
        ("0 0 * * *", "2024-01-01T00:00", "2024-01-02T00:00"),
        ("0 0 * * *", "2024-02-28T23:59", "2024-02-29T00:00"),
        ("30 9 * * 1-5", "2024-06-07T09:30", "2024-06-10T09:30"),
        ("0 0 1 * *", "2024-01-31T12:00", "2024-02-01T00:00"),
        ("0 0 31 * *", "2024-04-01T00:00", "2024-05-31T00:00"),
        ("0 0 29 2 *", "2023-03-01T00:00", "2024-02-29T00:00"),
        ("0 0 29 2 *", "1996-03-01T00:00", "2000-02-29T00:00"),
        ("0 0 29 2 *", "2096-03-01T00:00", "2104-02-29T00:00"),
        ("0 0 29 2 *", "1896-03-01T00:00", "1904-02-29T00:00"),
        ("0 0 13 * 5", "2024-09-01T00:00", "2024-09-06T00:00"),
        ("0 0 13 * 5", "2024-09-06T00:00", "2024-09-13T00:00"),
        ("0 0 15 * */2", "2024-09-02T00:00", "2024-09-03T00:00"),
        ("0 0 31 2 1", "2024-02-01T00:00", "2024-02-05T00:00"),
        ("0 0 * 2 1", "2024-02-26T00:00", "2025-02-03T00:00"),
        ("0 8 * * 0", "2024-09-02T00:00", "2024-09-08T08:00"),
        ("0 0 * * 6", "2024-09-01T00:00", "2024-09-07T00:00"),
        ("5-10/2 * * * *", "2024-01-01T00:07", "2024-01-01T00:09"),
        ("5-10/2 * * * *", "2024-01-01T00:09", "2024-01-01T01:05"),
        ("50/5 * * * *", "2024-01-01T00:56", "2024-01-01T01:50"),
        ("0,30 9,17 * * *", "2024-01-01T09:30", "2024-01-01T17:00"),
        ("0 0 1 */3 *", "2024-02-15T00:00", "2024-04-01T00:00"),
        ("  0   0 * * *  ", "2024-01-01T00:00", "2024-01-02T00:00"),
        ("05 07 * * *", "2024-01-01T00:00", "2024-01-01T07:05"),
        ("0 0 * * *", "0001-01-01T00:00", "0001-01-02T00:00"),
        ("0 12 31 12 *", "9999-12-31T11:59", "9999-12-31T12:00"),
        ("0 12 31 12 *", "9999-12-31T12:00", None),
        ("* * * * *", "9999-12-31T23:59", None),
        ("59 23 31 12 *", "2024-12-31T23:58", "2024-12-31T23:59"),
        # Month end with a weekday field: there is no April 31, the next Wednesday is May 1.
        ("0 0 * * 3", "2024-04-30T00:00", "2024-05-01T00:00"),
        ("0 0 15 * 3", "2024-04-30T00:00", "2024-05-01T00:00"),
        ("0 0 * * 4", "2023-02-28T00:00", "2023-03-02T00:00"),
    ],
)
def test_examples(expr, after, expected):
    assert cron_next(expr, after) == expected


@pytest.mark.parametrize(
    "expr, after",
    [
        # Starts are late enough that a day-by-day scan stays well under the time limit,
        # while a minute-by-minute scan (~1.5 billion steps) cannot finish.
        ("0 0 30 2 *", "7000-01-01T00:00"),
        ("0 0 31 4,6,9,11 *", "8000-01-01T00:00"),
        ("*/5 * 30,31 2 *", "7500-06-15T12:00"),
    ],
)
def test_never_matches(expr, after):
    assert cron_next(expr, after) is None


@pytest.mark.parametrize(
    "expr",
    [
        "* * * *", "* * * * * *", "", "60 * * * *", "* 24 * * *", "* * 0 * *", "* * 32 * *",
        "* * * 13 *", "* * * 0 *", "* * * * 7", "5-1 * * * *", "*/0 * * * *", "1-5/0 * * * *",
        "1,,2 * * * *", "1, * * * *", "a * * * *", "* * * JAN *", "0 0 * * MON", "*/ * * * *",
        "-1 * * * *", "1- * * * *", "*-5 * * * *", "+1 * * * *", "1-2-3 * * * *",
    ],
)
def test_invalid_expr(expr):
    with pytest.raises(ValueError):
        cron_next(expr, "2024-01-01T00:00")


@pytest.mark.parametrize(
    "after",
    [
        "2024-01-01 00:00", "2024-01-01T00:00:00", "2024-02-30T00:00", "2023-02-29T00:00",
        "2024-01-01T24:00", "2024-01-01T00:60", "0000-01-01T00:00", "2024-1-01T00:00",
        "2024-01-01t00:00", "2024-13-01T00:00", " 2024-01-01T00:00",
    ],
)
def test_invalid_after(after):
    with pytest.raises(ValueError):
        cron_next("* * * * *", after)


# ---- differential test against a minute-by-minute oracle over a short window ----

def _expand(field, lo, hi):
    out = set()
    for item in field.split(","):
        rng_part, _, step = item.partition("/")
        if rng_part == "*":
            a, b = lo, hi
        elif "-" in rng_part:
            a, b = map(int, rng_part.split("-"))
        else:
            a = int(rng_part)
            b = hi if step else a
        out.update(range(a, b + 1, int(step) if step else 1))
    return out


def _oracle(expr, after, window_minutes):
    f = expr.split()
    mins, hrs, doms, mons, dows = (_expand(x, lo, hi) for x, (lo, hi) in zip(f, [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]))
    t = datetime.strptime(after, "%Y-%m-%dT%H:%M")
    for _ in range(window_minutes):
        t += timedelta(minutes=1)
        dom_ok, dow_ok = t.day in doms, (t.weekday() + 1) % 7 in dows
        day_ok = (dom_ok or dow_ok) if (f[2] != "*" and f[4] != "*") else (dom_ok and dow_ok)
        if t.minute in mins and t.hour in hrs and t.month in mons and day_ok:
            return t.strftime("%Y-%m-%dT%H:%M")
    return None


_POOLS = [
    ["*", "0", "*/7", "5-20/5", "59", "0,30", "15/20"],
    ["*", "0", "23", "9-17", "*/6", "1,13"],
    ["*", "1", "15", "31", "29", "1-7", "*/10", "10-12"],
    ["*", "*", "2", "1-6", "*/2", "12"],
    ["*", "*", "0", "6", "1-5", "*/3", "3,5"],
]


def test_random_against_oracle():
    rng = random.Random(4)
    window = 45 * 24 * 60
    for _ in range(60):
        fields = [rng.choice(p) for p in _POOLS]
        if fields[2] == "31" and fields[3] == "2":
            fields[3] = "12"  # never-matching combo: would make the call scan to year 9999
        expr = " ".join(fields)
        start = datetime(2024, 1, 1) + timedelta(minutes=rng.randrange(3 * 365 * 24 * 60))
        after = start.strftime("%Y-%m-%dT%H:%M")
        want = _oracle(expr, after, window)
        got = cron_next(expr, after)
        if want is not None:
            assert got == want, (expr, after)
        else:
            limit = (start + timedelta(minutes=window)).strftime("%Y-%m-%dT%H:%M")
            assert got is None or got > limit, (expr, after, got)
