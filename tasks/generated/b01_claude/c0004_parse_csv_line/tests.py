import random

import pytest
from solution import parse_csv_line


@pytest.mark.parametrize(
    "line, delimiter, expected",
    [
        ('a,"b,c",d', ",", ["a", "b,c", "d"]),
        ('"say ""hi""";;x', ";", ['say "hi"', "", "x"]),
        ('"say ""hi"" now";;x', ";", ['say "hi" now', "", "x"]),
        ("", ",", [""]),
        ("a", ",", ["a"]),
        ("a,", ",", ["a", ""]),
        (",", ",", ["", ""]),
        ('""', ",", [""]),
        ('"",""', ",", ["", ""]),
        ("a, b ,c", ",", ["a", " b ", "c"]),
        ('"x""y"', ",", ['x"y']),
        ('""""', ",", ['"']),
        ('"a,b",', ",", ["a,b", ""]),
        ('1\t"two\tthree"\t4', "\t", ["1", "two\tthree", "4"]),
        ("a|b||c", "|", ["a", "b", "", "c"]),
        ('"multi;delim"', ";", ["multi;delim"]),
        ('a,b', ";", ["a,b"]),
    ],
)
def test_examples(line, delimiter, expected):
    assert list(parse_csv_line(line, delimiter)) == expected


def test_default_delimiter():
    assert list(parse_csv_line("x,y")) == ["x", "y"]


@pytest.mark.parametrize("line", ['"abc', 'a"b', '"a"b', '"a" ,b', ' "a"', 'a,"b', '"a""', 'x,y"'])
def test_malformed(line):
    with pytest.raises(ValueError):
        parse_csv_line(line, ",")


@pytest.mark.parametrize("delimiter", [",,", '"', "\n", "\r", ""])
def test_bad_delimiter(delimiter):
    with pytest.raises(ValueError):
        parse_csv_line("a", delimiter)


def _encode(fields, delim, rng):
    out = []
    for f in fields:
        if '"' in f or delim in f or rng.random() < 0.3:
            out.append('"' + f.replace('"', '""') + '"')
        else:
            out.append(f)
    return delim.join(out)


def test_round_trip_random():
    # Encoding per the rules and parsing back must return the original fields.
    rng = random.Random(19)
    for _ in range(200):
        delim = rng.choice([",", ";", "\t", "|"])
        fields = ["".join(rng.choice('ab ,;"|\tx') for _ in range(rng.randint(0, 5))) for _ in range(rng.randint(1, 6))]
        line = _encode(fields, delim, rng)
        assert list(parse_csv_line(line, delim)) == fields, (line, delim)
