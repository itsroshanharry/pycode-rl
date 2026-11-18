import random

import pytest
from solution import parse_ini


@pytest.mark.parametrize(
    "text, expected",
    [
        ("a=1\n[S]\nx = hello ;greeting\ny=a;b\n[S]\nX = 2", {"": {"a": "1"}, "S": {"x": "2", "y": "a;b"}}),
        ("", {}),
        ("; only a comment\n# another\n\n   \n", {}),
        ("[empty]", {"empty": {}}),
        ("[A]\n[a]\nk=v", {"A": {}, "a": {"k": "v"}}),
        ("  [  sp ace  ]  \n  Key  =  some value  ", {"sp ace": {"key": "some value"}}),
        ("k=a=b=c", {"": {"k": "a=b=c"}}),
        ("k=", {"": {"k": ""}}),
        ("k = v #c", {"": {"k": "v"}}),
        ("k = v#c", {"": {"k": "v#c"}}),
        ("k = v\t;tab comment", {"": {"k": "v"}}),
        ("k = ;all comment", {"": {"k": ""}}),
        ("k=1\nK=2\nk=3", {"": {"k": "3"}}),
        ("[S]\nurl = http://x/?a=1;b=2 ; note", {"S": {"url": "http://x/?a=1;b=2"}}),
        ("[S]\n; key=not\n#k2=no\nk=yes", {"S": {"k": "yes"}}),
    ],
)
def test_parse(text, expected):
    assert parse_ini(text) == expected


@pytest.mark.parametrize("text", ["[]", "[ ]", "[a]b]", "[a", "just text", "=value", " = v", "[x]\nnoequals"])
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_ini(text)


def test_random_generated_files():
    # Render random content with random spacing/comments; parsing must recover it.
    rng = random.Random(20)
    for _ in range(150):
        expected, lines = {}, []
        for s in range(rng.randint(0, 3)):
            name = rng.choice(["Main", "db", "x y", "S" + str(s)])
            lines.append(f"{' ' * rng.randint(0, 2)}[{' ' * rng.randint(0, 1)}{name}]")
            sec = expected.setdefault(name, {})
            for _ in range(rng.randint(0, 3)):
                key = rng.choice(["Host", "port", "Mode", "k1"])
                value = rng.choice(["", "1", "a;b", "x#y", "two words", "a=b"])
                comment = rng.choice(["", " ;note", "  # hi"])
                lines.append(f"{key}{' ' * rng.randint(0, 2)}={' ' * rng.randint(0, 2)}{value}{comment}")
                sec[key.lower()] = value
            if rng.random() < 0.3:
                lines.append(rng.choice(["", "; c", "# c"]))
        assert parse_ini("\n".join(lines)) == expected, lines
