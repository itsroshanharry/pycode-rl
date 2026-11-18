import random
from urllib.parse import quote_plus

import pytest
from solution import parse_query


@pytest.mark.parametrize(
    "query, expected",
    [
        ("a=1&b=two+words&a=%E2%82%AC", [("a", ["1", "€"]), ("b", ["two words"])]),
        ("flag&x=&&y==z", [("flag", [""]), ("x", [""]), ("y", ["=z"])]),
        ("", []),
        ("&&", []),
        ("a=1&a=2&a=3", [("a", ["1", "2", "3"])]),
        ("%41%42=%63", [("AB", ["c"])]),
        ("a+b=c+d", [("a b", ["c d"])]),
        ("k=%2B%26%3D", [("k", ["+&="])]),
        ("k=%e2%82%ac", [("k", ["€"])]),
        ("é=ü", [("é", ["ü"])]),
        ("k=a%20b+c", [("k", ["a b c"])]),
        ("b=1&a=2&b=3", [("b", ["1", "3"]), ("a", ["2"])]),
        ("k=%25", [("k", ["%"])]),
        ("x=1&y", [("x", ["1"]), ("y", [""])]),
    ],
)
def test_parse(query, expected):
    assert list(parse_query(query).items()) == expected


@pytest.mark.parametrize("query", ["a=%", "a=%4", "a=%G1", "=x", "a=%FF", "a=%C3", "%=1", "a=1&=2", "k=%%41"])
def test_invalid(query):
    with pytest.raises(ValueError):
        parse_query(query)


def test_random_round_trip():
    # Encode random keys/values with the standard library, parse back, compare.
    rng = random.Random(21)
    alphabet = "ab =&+%€é/?#"
    for _ in range(200):
        pairs = []
        for _ in range(rng.randint(0, 6)):
            key = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 4)))
            value = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 4)))
            pairs.append((key, value))
        query = "&".join(f"{quote_plus(k, safe='')}={quote_plus(v, safe='')}" for k, v in pairs)
        expected: dict = {}
        for k, v in pairs:
            expected.setdefault(k, []).append(v)
        assert list(parse_query(query).items()) == list(expected.items()), query
