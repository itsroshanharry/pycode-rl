import random

import pytest
from solution import billing_dates


@pytest.mark.parametrize(
    "anchor, count, expected",
    [
        ("2024-01-31", 4, ["2024-01-31", "2024-02-29", "2024-03-31", "2024-04-30"]),
        ("2023-11-15", 3, ["2023-11-15", "2023-12-15", "2024-01-15"]),
        ("2024-05-10", 0, []),
        ("2024-05-10", 1, ["2024-05-10"]),
        ("2023-01-30", 2, ["2023-01-30", "2023-02-28"]),
        ("2024-12-31", 3, ["2024-12-31", "2025-01-31", "2025-02-28"]),
        ("2024-03-31", 2, ["2024-03-31", "2024-04-30"]),
        ("2024-02-29", 13, ["2024-02-29", "2024-03-29", "2024-04-29", "2024-05-29", "2024-06-29", "2024-07-29",
                             "2024-08-29", "2024-09-29", "2024-10-29", "2024-11-29", "2024-12-29", "2025-01-29",
                             "2025-02-28"]),
        ("1900-01-29", 2, ["1900-01-29", "1900-02-28"]),
        ("2000-01-29", 2, ["2000-01-29", "2000-02-29"]),
        ("2023-08-31", 4, ["2023-08-31", "2023-09-30", "2023-10-31", "2023-11-30"]),
    ],
)
def test_examples(anchor, count, expected):
    assert list(billing_dates(anchor, count)) == expected


@pytest.mark.parametrize("anchor, count", [("2024-1-31", 2), ("2023-02-29", 2), ("20240131", 2), ("2024/01/31", 2), ("2024-01-31", -1), ("", 1)])
def test_invalid(anchor, count):
    with pytest.raises(ValueError):
        billing_dates(anchor, count)


def _days_in_month(y, m):
    if m == 2:
        return 29 if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else 28
    return 30 if m in (4, 6, 9, 11) else 31


def _oracle(anchor, count):
    y, m, d = (int(p) for p in anchor.split("-"))
    out = []
    for _ in range(count):
        out.append(f"{y:04d}-{m:02d}-{min(d, _days_in_month(y, m)):02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def test_random_against_oracle():
    rng = random.Random(5)
    for _ in range(200):
        y, m = rng.randint(1890, 2110), rng.randint(1, 12)
        d = rng.randint(1, _days_in_month(y, m))
        anchor = f"{y:04d}-{m:02d}-{d:02d}"
        n = rng.randint(0, 30)
        assert list(billing_dates(anchor, n)) == _oracle(anchor, n), (anchor, n)
