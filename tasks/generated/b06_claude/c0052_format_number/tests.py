import random
from decimal import ROUND_HALF_EVEN, Decimal, localcontext

import pytest
from solution import format_number


@pytest.mark.parametrize(
    "args, expected",
    [
        (("1234567.891", ",", ".", [3], 2), "1.234.567,89"),
        (("123456789", ".", ",", [3, 2], 0), "12,34,56,789"),
        (("1234567890", ".", ",", [4, 3], 0), "123,456,7890"),
        (("1234", ".", ",", [1], 0), "1,2,3,4"),
        (("1000", ".", " ", [], 0), "1000"),
        (("1000", ".", ",", [3], 0), "1,000"),
        (("999", ".", ",", [3], 0), "999"),
        (("-0.004", ".", ",", [3], 2), "0.00"),
        (("-0.005", ".", ",", [3], 2), "0.00"),
        (("-0.015", ".", ",", [3], 2), "-0.02"),
        (("-0.006", ".", ",", [3], 2), "-0.01"),
        (("2.5", ".", ",", [3], 0), "2"),
        (("3.5", ".", ",", [3], 0), "4"),
        (("-2.5", ".", ",", [3], 0), "-2"),
        (("0.5", ".", ",", [3], 0), "0"),
        (("-0.5", ".", ",", [3], 0), "0"),
        (("2.50000001", ".", ",", [3], 0), "3"),
        (("999.995", ".", ",", [3], 2), "1,000.00"),
        (("0.125", ".", ",", [3], 2), "0.12"),
        (("0.135", ".", ",", [3], 2), "0.14"),
        (("7", ",", ".", [3], 3), "7,000"),
        (("0007.10", ".", ",", [3], 1), "7.1"),
        (("0", ".", ",", [3], 0), "0"),
        (("-0", ".", ",", [3], 2), "0.00"),
        (("12345678901234567890123456789012345.5", ".", ",", [3], 0), "12,345,678,901,234,567,890,123,456,789,012,346"),
        (("1234567.5", "٫", "٬", [3], 0), "1٬234٬568"),
        (("1234567", ".", " ", [3], 1), "1 234 567.0"),
        (("1234567", "<dec>", "<grp>", [2, 3], 1), "12<grp>345<grp>67<dec>0"),
        (("100000", ".", ",", [3, 2], 0), "1,00,000"),
        (("-9876543.21", ".", "'", [3], 1), "-9'876'543.2"),
    ],
)
def test_examples(args, expected):
    assert format_number(*args) == expected


@pytest.mark.parametrize(
    "args",
    [
        ("1e5", ".", ",", [3], 0), ("+1", ".", ",", [3], 0), (".5", ".", ",", [3], 0), ("1.", ".", ",", [3], 0),
        ("", ".", ",", [3], 0), (" 1", ".", ",", [3], 0), ("1 ", ".", ",", [3], 0), ("１", ".", ",", [3], 0),
        ("1,000", ".", ",", [3], 0), ("--1", ".", ",", [3], 0), ("1.2.3", ".", ",", [3], 0),
        ("1", ".", ",", [3], -1), ("1", ".", ",", [3, 0], 0), ("1", ".", ".", [3], 0), ("1", "", ",", [3], 0),
        ("1", ".", "", [3], 0),
    ],
)
def test_invalid(args):
    with pytest.raises(ValueError):
        format_number(*args)


def _oracle(value, dm, gs, grouping, f):
    with localcontext() as ctx:
        ctx.prec = 200
        q = Decimal(value).quantize(Decimal(1).scaleb(-f), rounding=ROUND_HALF_EVEN)
    neg = q < 0
    s = format(abs(q), "f")
    ip, _, fp = s.partition(".")
    groups, i, rest = [], 0, ip
    while grouping and len(rest) > grouping[min(i, len(grouping) - 1)]:
        g = grouping[min(i, len(grouping) - 1)]
        groups.insert(0, rest[-g:])
        rest, i = rest[:-g], i + 1
    groups.insert(0, rest)
    out = ("-" if neg else "") + gs.join(groups)
    return out + (dm + fp if f else "")


def test_random_against_oracle():
    rng = random.Random(30)
    for _ in range(400):
        ip = str(rng.randint(0, 10 ** rng.randint(0, 15)))
        value = ("-" if rng.random() < 0.4 else "") + ip
        if rng.random() < 0.7:
            value += "." + "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 6)))
        grouping = rng.choice([[], [3], [3, 2], [2], [4, 3, 1]])
        f = rng.randint(0, 4)
        assert format_number(value, ".", ",", grouping, f) == _oracle(value, ".", ",", grouping, f), (value, grouping, f)
