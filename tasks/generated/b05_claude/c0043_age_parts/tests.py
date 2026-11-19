import calendar
import random
from datetime import date, timedelta

import pytest
from solution import age_parts


@pytest.mark.parametrize(
    "birth, on, expected",
    [
        ("2020-02-29", "2023-02-28", (2, 364)),
        ("2020-02-29", "2023-03-01", (3, 0)),
        ("2020-02-29", "2020-02-29", (0, 0)),
        ("2020-02-29", "2020-03-01", (0, 1)),
        ("2020-02-29", "2021-02-28", (0, 365)),
        ("2020-02-29", "2021-03-01", (1, 0)),
        ("2020-02-29", "2024-02-28", (3, 364)),
        ("2020-02-29", "2024-02-29", (4, 0)),
        ("2020-02-29", "2024-03-01", (4, 1)),
        ("2096-02-29", "2100-02-28", (3, 364)),
        ("2096-02-29", "2100-03-01", (4, 0)),
        ("1990-06-15", "2024-06-14", (33, 365)),
        ("1990-06-15", "2024-06-15", (34, 0)),
        ("1990-06-15", "2024-12-31", (34, 199)),
        ("2023-03-01", "2024-02-29", (0, 365)),
        ("2023-03-01", "2024-03-01", (1, 0)),
        ("2000-12-31", "2001-12-30", (0, 364)),
        ("2000-12-31", "2001-12-31", (1, 0)),
        ("2000-01-01", "2000-01-01", (0, 0)),
        ("0001-01-01", "9999-12-31", (9998, 364)),
    ],
)
def test_examples(birth, on, expected):
    assert tuple(age_parts(birth, on)) == expected


@pytest.mark.parametrize(
    "birth, on",
    [
        ("2024-01-02", "2024-01-01"),
        ("2023-02-29", "2024-01-01"),
        ("2024-01-01", "2024-13-01"),
        ("2024-1-01", "2024-02-01"),
        ("0000-01-01", "2024-01-01"),
        ("2024-01-01", "2024/02/01"),
        (" 2024-01-01", "2024-02-01"),
        ("2024-01-01", "2024-02-01T00:00"),
        ("2024-04-31", "2024-05-01"),
        ("２０２４-01-01", "2024-02-01"),
        ("2024-01-01", ""),
    ],
)
def test_invalid(birth, on):
    with pytest.raises(ValueError):
        age_parts(birth, on)


def _bday(b, y):
    if (b.month, b.day) == (2, 29) and not calendar.isleap(y):
        return date(y, 3, 1)
    return date(y, b.month, b.day)


def test_random_against_oracle():
    rng = random.Random(9)
    for _ in range(400):
        b = date(1900, 1, 1) + timedelta(days=rng.randrange(80000))
        if rng.random() < 0.25:
            y = rng.choice([1904, 1960, 2000, 2024, 2096])
            b = date(y, 2, 29)
        d = b + timedelta(days=rng.randrange(0, 30000))
        k = 0
        while _bday(b, b.year + k + 1) <= d:
            k += 1
        want = (k, (d - _bday(b, b.year + k)).days if k else (d - b).days)
        assert tuple(age_parts(b.isoformat(), d.isoformat())) == want, (b, d)
