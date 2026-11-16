import pytest
from solution import parse_duration


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1h30m", 5400),
        (" 2d 4h 5s ", 187205),
        ("45s", 45),
        ("1m", 60),
        ("1d", 86400),
        ("0s", 0),
        ("1h 0m 5s", 3605),
        ("10d", 864000),
        ("1d1s", 86401),
        ("007m", 420),
        ("3h  15m", 11700),
        ("  12m  ", 720),
        ("1d 23h 59m 59s", 172799),
        ("999999999d", 86399999913600),
        ("100h", 360000),
    ],
)
def test_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize(
    "text",
    ["", "   ", "1x", "h", "5m1h", "1h1h", "1 h", "-1h", "+2m", "1.5h", "1H",
     "1h,30m", "10", "m30", "1s 1m", "1d 1d", "1h30", "h1"],
)
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)
