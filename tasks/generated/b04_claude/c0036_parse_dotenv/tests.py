import random

import pytest
from solution import parse_dotenv


@pytest.mark.parametrize(
    "text, expected",
    [
        ('export A=1 # one\nB="x\\ty"\nC=\'$HOME\'\nA=2', {"A": "2", "B": "x\ty", "C": "$HOME"}),
        ("", {}),
        ("\n   \n# comment\n  # indented comment", {}),
        ("A=", {"A": ""}),
        ("A=   ", {"A": ""}),
        ("A = spaced value  ", {"A": "spaced value"}),
        ("A=a#b", {"A": "a#b"}),
        ("A=a #b", {"A": "a"}),
        ("A=a\t#b", {"A": "a\t#b"}),
        ("A='x # y'", {"A": "x # y"}),
        ('A="x # y" # real comment', {"A": "x # y"}),
        ("A='a\\nb'", {"A": "a\\nb"}),
        ('A="a\\nb\\\\c\\"d"', {"A": 'a\nb\\c"d'}),
        ("export   B=2", {"B": "2"}),
        ("exportC=3", {"exportC": "3"}),
        ("_x9=ok", {"_x9": "ok"}),
        ("A=\"\"", {"A": ""}),
        ("A=''   ", {"A": ""}),
        ("A=1\nA=2\nA=3", {"A": "3"}),
        ("A=x=y", {"A": "x=y"}),
    ],
)
def test_parse(text, expected):
    assert parse_dotenv(text) == expected


@pytest.mark.parametrize(
    "text",
    ["A", "=x", "1A=x", "A-B=x", "A='open", 'A="open', 'A="bad\\q"', "A='x' y", 'A="x"y', "export A",
     "A B=1", 'A="x\\"', "export\tA=1"],
)
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_dotenv(text)


def _render(value, rng):
    style = rng.choice(["single", "double", "plain"])
    if style == "single" and "'" not in value and "\n" not in value:
        return "'" + value + "'"
    if style == "double" or "'" in value:
        enc = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t")
        return '"' + enc + '"'
    return value


def test_random_round_trip():
    rng = random.Random(24)
    for _ in range(200):
        expected, lines = {}, []
        for i in range(rng.randint(0, 6)):
            name = rng.choice(["A", "B_1", "_c", "DB_URL"])
            value = "".join(rng.choice(["a", "1", " ", "#", "'", '"', "\\", "\t", "\n", "="]) for _ in range(rng.randint(0, 5)))
            plain_ok = value == value.strip() and " #" not in value and not value.startswith(("'", '"')) and "\n" not in value and "\t" not in value and value != ""
            rendered = _render(value, rng) if not plain_ok or rng.random() < 0.6 else value
            if rendered == value and not plain_ok:
                continue
            prefix = rng.choice(["", "export ", "  "])
            lines.append(f"{prefix}{name}{rng.choice(['=', ' = ', '= '])}{rendered}{rng.choice(['', '  # note'])}")
            expected[name] = value
            if rng.random() < 0.2:
                lines.append(rng.choice(["", "# c", "   "]))
        assert parse_dotenv("\n".join(lines)) == expected, lines
