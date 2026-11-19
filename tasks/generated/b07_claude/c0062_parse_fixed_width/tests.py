import pytest
from solution import parse_fixed_width

LAYOUT = [("name", 1, 10, "str"), ("amount", 11, 8, "cents"), ("day", 19, 8, "date"), ("ok", 27, 1, "flag")]


@pytest.mark.parametrize(
    "record, layout, expected",
    [
        ("ACME      -001234520240229Y", LAYOUT, {"name": "ACME", "amount": "-123.45", "day": "2024-02-29", "ok": True}),
        ("ACME      -001234520240229Y extra", LAYOUT, {"name": "ACME", "amount": "-123.45", "day": "2024-02-29", "ok": True}),
        ("  lead\t".ljust(10) + "00000005" + " " * 8 + "N", LAYOUT, {"name": "  lead\t", "amount": "0.05", "day": None, "ok": False}),
        ("          -000000000000000  ", LAYOUT, {"name": "", "amount": "0.00", "day": None, "ok": None}),
        ("x" * 10 + "        " + "00000000" + "Y", LAYOUT, {"name": "xxxxxxxxxx", "amount": None, "day": None, "ok": True}),
        ("   42", [("n", 1, 5, "int")], {"n": 42}),
        ("42   ", [("n", 1, 5, "int")], {"n": 42}),
        (" -042", [("n", 1, 5, "int")], {"n": -42}),
        ("-0000", [("n", 1, 5, "int")], {"n": 0}),
        ("     ", [("n", 1, 5, "int")], {"n": None}),
        ("12345", [("n", 1, 5, "cents")], {"n": "123.45"}),
        ("    5", [("n", 1, 5, "cents")], {"n": "0.05"}),
        ("-0001", [("n", 1, 5, "cents")], {"n": "-0.01"}),
        ("-0000", [("n", 1, 5, "cents")], {"n": "0.00"}),
        ("abcdef", [("a", 1, 3, "str"), ("b", 2, 3, "str"), ("c", 6, 1, "str")], {"a": "abc", "b": "bcd", "c": "f"}),
        ("abc", [("c", 3, 1, "str"), ("a", 1, 1, "str")], {"c": "c", "a": "a"}),
        ("19991231", [("d", 1, 8, "date")], {"d": "1999-12-31"}),
        ("ab  ", [("s", 1, 4, "str")], {"s": "ab"}),
        ("ab\t ", [("s", 1, 4, "str")], {"s": "ab\t"}),
    ],
)
def test_examples(record, layout, expected):
    got = parse_fixed_width(record, layout)
    assert got == expected
    assert list(got) == [e[0] for e in layout]


@pytest.mark.parametrize(
    "record, layout",
    [
        ("short", LAYOUT),
        ("abc", [("s", 1, 5, "str")]),
        ("abcd", [("s", 1, 2, "str"), ("t", 4, 2, "str")]),
        ("abc", [("a", 0, 2, "str")]),
        ("abc", [("a", 1, 0, "str")]),
        ("abc", [("a", 1, 2, "text")]),
        ("abc", [("a", 1, 1, "str"), ("a", 2, 1, "str")]),
        ("12a45", [("n", 1, 5, "int")]),
        ("1 2  ", [("n", 1, 5, "int")]),
        ("+0042", [("n", 1, 5, "int")]),
        ("--042", [("n", 1, 5, "int")]),
        ("  -  ", [("n", 1, 5, "int")]),
        ("0x1F ", [("n", 1, 5, "int")]),
        ("４２   ", [("n", 1, 5, "int")]),
        ("\t42  ", [("n", 1, 5, "int")]),
        ("12.45", [("n", 1, 5, "cents")]),
        ("20230229", [("d", 1, 8, "date")]),
        ("2023-1-1", [("d", 1, 8, "date")]),
        ("2023123 ", [("d", 1, 8, "date")]),
        ("20231301", [("d", 1, 8, "date")]),
        ("y", [("f", 1, 1, "flag")]),
        ("1", [("f", 1, 1, "flag")]),
        ("YY", [("f", 1, 2, "flag")]),
    ],
)
def test_invalid(record, layout):
    with pytest.raises(ValueError):
        parse_fixed_width(record, layout)
