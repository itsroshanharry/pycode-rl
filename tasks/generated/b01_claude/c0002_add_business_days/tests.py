import datetime as dt
import random

import pytest
from solution import add_business_days


@pytest.mark.parametrize(
    "start, n, holidays, expected",
    [
        ("2024-03-08", 1, [], "2024-03-11"),
        ("2024-12-24", 2, ["2024-12-25", "2024-12-26"], "2024-12-30"),
        ("2024-03-08", 0, [], "2024-03-08"),
        ("2024-03-09", 0, [], "2024-03-11"),
        ("2024-03-09", 1, [], "2024-03-11"),
        ("2024-03-11", -1, [], "2024-03-08"),
        ("2024-03-10", -1, [], "2024-03-08"),
        ("2024-02-28", 2, ["2024-02-29"], "2024-03-04"),
        ("2023-02-28", 1, [], "2023-03-01"),
        ("2024-03-08", 1, ["2024-03-09", "2024-03-10"], "2024-03-11"),
        ("2024-03-08", 1, ["2024-03-11", "2024-03-11"], "2024-03-12"),
        ("2025-12-31", 1, ["2026-01-01"], "2026-01-02"),
        ("2024-03-11", 5, [], "2024-03-18"),
        ("2024-12-27", -2, ["2024-12-25", "2024-12-26"], "2024-12-23"),
        ("2024-03-11", 0, ["2024-03-11"], "2024-03-12"),
    ],
)
def test_examples(start, n, holidays, expected):
    assert add_business_days(start, n, holidays) == expected


@pytest.mark.parametrize(
    "start, holidays",
    [("2024-3-8", []), ("2024/03/08", []), ("20240308", []), ("2024-02-30", []),
     ("2024-03-08", ["2024-13-01"]), ("2024-03-08", [""]), ("", [])],
)
def test_invalid(start, holidays):
    with pytest.raises(ValueError):
        add_business_days(start, 1, holidays)


def _oracle(start, n, holidays):
    # List business days by ordinal number (ordinal % 7: 1 = Monday ... 0 = Sunday),
    # then index into the list.
    s = dt.date.fromisoformat(start).toordinal()
    off = {dt.date.fromisoformat(h).toordinal() for h in holidays}

    def ok(o):
        return o % 7 not in (6, 0) and o not in off

    if n == 0:
        return dt.date.fromordinal(next(o for o in range(s, s + 400) if ok(o))).isoformat()
    span = range(s + 1, s + 3 * abs(n) + 400) if n > 0 else range(s - 1, s - 3 * abs(n) - 400, -1)
    days = [o for o in span if ok(o)]
    return dt.date.fromordinal(days[abs(n) - 1]).isoformat()


def test_random_against_oracle():
    rng = random.Random(3)
    base = dt.date(2023, 1, 1).toordinal()
    for _ in range(150):
        start = dt.date.fromordinal(base + rng.randint(0, 1200))
        holidays = [(start + dt.timedelta(days=rng.randint(-30, 30))).isoformat() for _ in range(rng.randint(0, 8))]
        n = rng.randint(-40, 40)
        assert add_business_days(start.isoformat(), n, holidays) == _oracle(start.isoformat(), n, holidays), (start, n, holidays)


def test_large_n():
    assert add_business_days("2000-01-03", 10_000, []) == _oracle("2000-01-03", 10_000, [])
    assert add_business_days("2000-01-03", -10_000, ["1990-01-01"]) == _oracle("2000-01-03", -10_000, ["1990-01-01"])
