import datetime as dt
import random

import pytest
from solution import week_label


@pytest.mark.parametrize(
    "date, start, expected",
    [
        ("2021-01-03", 0, "2020-W53"),
        ("2021-01-03", 6, "2021-W01"),
        ("2024-12-30", 0, "2025-W01"),
        ("2024-12-29", 0, "2024-W52"),
        ("2026-01-01", 0, "2026-W01"),
        ("2027-01-03", 0, "2026-W53"),
        ("2020-12-31", 0, "2020-W53"),
        ("2024-01-01", 0, "2024-W01"),
        ("2024-03-15", 0, "2024-W11"),
        ("2023-01-01", 6, "2023-W01"),
        ("2022-01-01", 5, "2022-W01"),
        ("2025-12-28", 6, "2025-W53"),
        ("1900-01-01", 0, "1900-W01"),
        ("2100-12-31", 4, "2101-W01"),
    ],
)
def test_examples(date, start, expected):
    assert week_label(date, start) == expected


def test_default_week_start_is_monday():
    assert week_label("2021-01-03") == "2020-W53"


@pytest.mark.parametrize("date, start", [("2021-1-03", 0), ("20210103", 0), ("2021-02-29", 0), ("2021-01-03", 7), ("2021-01-03", -1)])
def test_invalid(date, start):
    with pytest.raises(ValueError):
        week_label(date, start)


def _oracle(d, start):
    # 4-day rule: a week belongs to the year that contains its 4th day.
    block = d - dt.timedelta(days=(d.weekday() - start) % 7)
    year = (block + dt.timedelta(days=3)).year
    first = dt.date(year, 1, 1)
    first_block = first - dt.timedelta(days=(first.weekday() - start) % 7)
    if (first_block + dt.timedelta(days=3)).year != year:
        first_block += dt.timedelta(days=7)
    return f"{year:04d}-W{(block - first_block).days // 7 + 1:02d}"


def test_iso_matches_standard_library():
    rng = random.Random(1)
    for _ in range(300):
        d = dt.date(1901, 1, 1) + dt.timedelta(days=rng.randint(0, 72000))
        y, w, _ = d.isocalendar()
        assert week_label(d.isoformat(), 0) == f"{y:04d}-W{w:02d}"


def test_all_week_starts_against_oracle():
    rng = random.Random(2)
    for _ in range(400):
        d = dt.date(1901, 1, 1) + dt.timedelta(days=rng.randint(0, 72000))
        if rng.random() < 0.5:  # concentrate on the year boundary
            d = dt.date(rng.randint(1901, 2099), rng.choice([1, 12]), rng.choice([1, 2, 3, 4, 5, 28, 29, 30, 31]))
        s = rng.randint(0, 6)
        assert week_label(d.isoformat(), s) == _oracle(d, s), (d, s)
