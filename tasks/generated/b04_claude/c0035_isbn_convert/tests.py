import random

import pytest
from solution import isbn_convert


@pytest.mark.parametrize(
    "isbn, expected",
    [
        ("0-306-40615-2", "9780306406157"),
        ("978 0 306 40615 7", "0306406152"),
        ("0306406152", "9780306406157"),
        ("9780306406157", "0306406152"),
        ("080442957X", "9780804429573"),
        ("080442957x", "9780804429573"),
        ("9780804429573", "080442957X"),
        ("0-8044-2957-X", "9780804429573"),
        ("000000000-0", "9780000000002"),
        ("9780000000002", "0000000000"),
    ],
)
def test_convert(isbn, expected):
    assert isbn_convert(isbn) == expected


@pytest.mark.parametrize(
    "isbn",
    ["", "030640615", "03064061522", "0306406153", "9780306406158", "9790306406156", "X306406152",
     "03064X6152", "97803064061X7", "0306406152 ".replace(" ", "_"), "０306406152", "0.306406152", "978030640615"],
)
def test_invalid(isbn):
    with pytest.raises(ValueError):
        isbn_convert(isbn)


def _c10(nine):
    for c in range(11):
        if (sum(int(d) * (10 - i) for i, d in enumerate(nine)) + c) % 11 == 0:
            return "X" if c == 10 else str(c)


def _c13(twelve):
    for c in range(10):
        if (sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(twelve)) + c) % 10 == 0:
            return str(c)


def test_random_round_trips():
    rng = random.Random(14)
    for _ in range(200):
        nine = "".join(rng.choice("0123456789") for _ in range(9))
        ten = nine + _c10(nine)
        thirteen = "978" + nine + _c13("978" + nine)
        assert isbn_convert(ten) == thirteen
        assert isbn_convert(thirteen) == ten
        hyphenated = f"{ten[0]}-{ten[1:4]}-{ten[4:9]}-{ten[9]}"
        assert isbn_convert(hyphenated) == thirteen
