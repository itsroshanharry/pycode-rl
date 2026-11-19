import random
from fractions import Fraction

import pytest
from solution import convert_base


@pytest.mark.parametrize(
    "args, expected",
    [
        (("-1a.8", 16, 2, 4), "-11010.1000"),
        (("0.1", 10, 2, 8), "0.00011001"),
        (("255", 10, 16, 0), "ff"),
        (("FF", 16, 10, 0), "255"),
        (("Zz", 36, 10, 0), "1295"),
        (("0", 10, 2, 0), "0"),
        (("000", 7, 3, 0), "0"),
        (("0007", 10, 2, 0), "111"),
        (("-0", 10, 10, 2), "0.00"),
        (("-0.01", 10, 10, 1), "0.0"),
        (("-0.01", 10, 10, 2), "-0.01"),
        (("-0.8", 16, 2, 2), "-0.10"),
        (("-0.8", 16, 2, 0), "0"),
        (("-5.5", 10, 10, 0), "-5"),
        (("0.999", 10, 10, 2), "0.99"),
        (("0.1", 3, 10, 6), "0.333333"),
        (("0.2", 3, 10, 4), "0.6666"),
        (("1.5", 10, 10, 3), "1.500"),
        (("10", 2, 36, 0), "2"),
        (("35", 10, 36, 0), "z"),
        (("36", 10, 36, 0), "10"),
        (("123456789012345678901234567890", 10, 36, 0), "byw97um9s91dlz68tsi"),
        (("0.000000000000000000001", 10, 2, 3), "0.000"),
        (("-0.000000000000000000001", 10, 2, 3), "0.000"),
        (("-0.000000000000000000001", 10, 2, 70), "-0." + "0" * 69 + "1"),
        (("1", 2, 2, 0), "1"),
        (("11.11", 2, 10, 4), "3.7500"),
    ],
)
def test_examples(args, expected):
    assert convert_base(*args) == expected


@pytest.mark.parametrize(
    "args",
    [
        ("2", 2, 10, 0), ("g", 16, 10, 0), ("1.2", 2, 10, 0), ("", 10, 2, 0), ("-", 10, 2, 0), (".5", 10, 2, 0),
        ("5.", 10, 2, 0), ("+5", 10, 2, 0), (" 5", 10, 2, 0), ("1_0", 10, 2, 0), ("0x1f", 16, 10, 0),
        ("５", 10, 2, 0), ("٥", 10, 2, 0), ("--5", 10, 2, 0), ("1.2.3", 10, 2, 0),
        ("5", 1, 10, 0), ("0", 1, 10, 0), ("0", 10, 1, 0), ("5", 10, 37, 0), ("5", 37, 10, 0), ("5", 10, 0, 0), ("5", 10, 2, -1),
    ],
)
def test_invalid(args):
    with pytest.raises(ValueError):
        convert_base(*args)


_D = "0123456789abcdefghijklmnopqrstuvwxyz"


def _oracle(number, fb, tb, fd):
    neg = number.startswith("-")
    ip, _, fp = number.lstrip("-").partition(".")
    value = Fraction(int(ip, fb)) + (Fraction(int(fp, fb), fb ** len(fp)) if fp else 0)
    scaled = int(value * tb ** fd)  # truncate toward zero (value >= 0)
    digits = ""
    while scaled:
        scaled, d = divmod(scaled, tb)
        digits = _D[d] + digits
    digits = digits.rjust(fd + 1, "0")
    ipart, fpart = digits[: len(digits) - fd], digits[len(digits) - fd:]
    out = ipart + ("." + fpart if fd else "")
    return ("-" + out) if neg and set(ipart + fpart) != {"0"} else out


def test_random_against_oracle():
    rng = random.Random(79)
    for _ in range(500):
        fb, tb = rng.randint(2, 36), rng.randint(2, 36)
        ip = "".join(rng.choice(_D[:fb]) for _ in range(rng.randint(1, 8)))
        num = ("-" if rng.random() < 0.4 else "") + ip
        if rng.random() < 0.7:
            num += "." + "".join(rng.choice(_D[:fb]) for _ in range(rng.randint(1, 6)))
        if rng.random() < 0.3:
            num = num.upper()
        fd = rng.randint(0, 8)
        assert convert_base(num, fb, tb, fd) == _oracle(num.lower(), fb, tb, fd), (num, fb, tb, fd)
