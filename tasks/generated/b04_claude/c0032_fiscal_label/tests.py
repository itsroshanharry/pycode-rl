import datetime as dt
import random

import pytest
from solution import fiscal_label


@pytest.mark.parametrize(
    "date, start, expected",
    [
        ("2024-05-10", 4, "FY2025-Q1"),
        ("2024-03-31", 4, "FY2024-Q4"),
        ("2024-04-01", 4, "FY2025-Q1"),
        ("2024-07-01", 4, "FY2025-Q2"),
        ("2024-12-31", 4, "FY2025-Q3"),
        ("2025-01-01", 4, "FY2025-Q4"),
        ("2024-01-15", 1, "FY2024-Q1"),
        ("2024-12-15", 1, "FY2024-Q4"),
        ("2023-10-01", 10, "FY2024-Q1"),
        ("2023-09-30", 10, "FY2023-Q4"),
        ("2024-02-29", 2, "FY2025-Q1"),
        ("2024-01-31", 2, "FY2024-Q4"),
        ("2024-12-01", 12, "FY2025-Q1"),
        ("2024-11-30", 12, "FY2024-Q4"),
        ("2024-03-01", 12, "FY2024-Q2"),
    ],
)
def test_examples(date, start, expected):
    assert fiscal_label(date, start) == expected


@pytest.mark.parametrize("date, start", [("2024-5-10", 4), ("2023-02-29", 4), ("20240510", 4), ("2024-05-10", 0), ("2024-05-10", 13)])
def test_invalid(date, start):
    with pytest.raises(ValueError):
        fiscal_label(date, start)


def _oracle(d, start):
    # Walk back to the first day of the fiscal year containing d, then count months.
    y, m = d.year, d.month
    months = 0
    while m != start:
        m -= 1
        months += 1
        if m == 0:
            m, y = 12, y - 1
    end_year = y if start == 1 else y + 1
    return f"FY{end_year}-Q{months // 3 + 1}"


def test_random_against_oracle():
    rng = random.Random(8)
    for _ in range(300):
        d = dt.date(1990, 1, 1) + dt.timedelta(days=rng.randint(0, 20000))
        s = rng.randint(1, 12)
        assert fiscal_label(d.isoformat(), s) == _oracle(d, s), (d, s)
