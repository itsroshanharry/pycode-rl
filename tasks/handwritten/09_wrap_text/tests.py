import random
import string

import pytest
from solution import wrap_text


@pytest.mark.parametrize(
    "text, width, expected",
    [
        ("the quick brown fox", 10, ["the quick", "brown fox"]),
        ("abcdefghij kl", 4, ["abcd", "efgh", "ij", "kl"]),
        ("", 5, []),
        ("   \n\t ", 3, []),
        ("hello", 5, ["hello"]),
        ("hello", 4, ["hell", "o"]),
        ("a b c d", 3, ["a b", "c d"]),
        ("a  b\n\nc", 10, ["a b c"]),
        ("abcdef g", 4, ["abcd", "ef g"]),
        ("a bcdefgh", 4, ["a", "bcde", "fgh"]),
        ("one two", 1, ["o", "n", "e", "t", "w", "o"]),
        ("xx yy zz", 5, ["xx yy", "zz"]),
        ("exactly ten", 11, ["exactly ten"]),
        ("exactly ten", 10, ["exactly", "ten"]),
    ],
)
def test_examples(text, width, expected):
    assert list(wrap_text(text, width)) == expected


def _chunks(text, width):
    out = []
    for w in text.split():
        out += [w[i : i + width] for i in range(0, len(w), width)]
    return out


def test_random_properties():
    # Checks the specification directly instead of comparing to one implementation.
    rng = random.Random(5)
    alphabet = string.ascii_lowercase[:6] + "  \n"
    for _ in range(150):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 60)))
        width = rng.randint(1, 12)
        lines = list(wrap_text(text, width))
        tokens = [t for line in lines for t in line.split(" ")]
        assert tokens == _chunks(text, width), (text, width, lines)  # same words, same order
        for line in lines:
            assert 1 <= len(line) <= width and "  " not in line and line == line.strip()
        for a, b in zip(lines, lines[1:]):  # greedy: the next word did not fit
            assert len(a) + 1 + len(b.split(" ")[0]) > width, (text, width, lines)
