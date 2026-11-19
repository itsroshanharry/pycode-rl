import random
import re

import pytest
from solution import slugify

DE = {"ü": "ue", "ß": "ss", "ö": "oe"}


@pytest.mark.parametrize(
    "title, translit, max_len, expected",
    [
        ("Grüße aus Köln!", DE, 50, "gruesse-aus-koeln"),
        ("The quick brown fox", {}, 14, "the-quick"),
        ("The quick brown fox", {}, 15, "the-quick-brown"),
        ("The quick brown fox", {}, 19, "the-quick-brown-fox"),
        ("Hello, World!", {}, 50, "hello-world"),
        ("ÄRGER", {"ä": "ae"}, 50, "rger"),
        ("ÄRGER", {"Ä": "Ae"}, 50, "aerger"),
        ("Kelvin", {}, 20, "elvin"),
        ("ǅemal", {}, 20, "emal"),
        ("supercalifragilistic word", {}, 5, "super"),
        ("--a--b--", {}, 10, "a-b"),
        ("", {}, 5, ""),
        ("!!! ???", {}, 5, ""),
        ("a&b", {"&": " and "}, 20, "a-and-b"),
        ("a&b", {"&": "&"}, 20, "a-b"),
        ("x", {"x": "Y"}, 20, "y"),
        ("ab", {"a": "b", "b": "c"}, 20, "bc"),
        ("Top 10 Lists of 2024", {}, 50, "top-10-lists-of-2024"),
        ("ＡＢＣ abc", {}, 50, "abc"),
        ("café au lait", {}, 50, "caf-au-lait"),
        ("a b c", {}, 1, "a"),
        ("ab cd", {}, 1, "a"),
        ("ab cd", {}, 3, "ab"),
        ("ab cd", {}, 4, "ab"),
        ("ab cd", {}, 5, "ab-cd"),
        ("MiXeD_CaSe-Words", {}, 50, "mixed-case-words"),
        ("tab\there\nnew", {}, 50, "tab-here-new"),
    ],
)
def test_examples(title, translit, max_len, expected):
    assert slugify(title, translit, max_len) == expected


@pytest.mark.parametrize("max_len", [0, -3])
def test_invalid(max_len):
    with pytest.raises(ValueError):
        slugify("abc", {}, max_len)


def _oracle(title, translit, max_len):
    s = ""
    for c in title:
        s += translit[c] if c in translit else c
    words, cur = [], ""
    for c in s:
        low = c.lower() if c.isascii() else c
        if low.isascii() and (low.isdigit() or "a" <= low <= "z"):
            cur += low
        else:
            if cur:
                words.append(cur)
            cur = ""
    if cur:
        words.append(cur)
    full = "-".join(words)
    if len(full) <= max_len:
        return full
    for k in range(len(words), 0, -1):
        cand = "-".join(words[:k])
        if len(cand) <= max_len:
            return cand
    return words[0][:max_len]


def test_random_against_oracle():
    rng = random.Random(18)
    alphabet = "abcXYZ019 -_.!éÜßK"
    for _ in range(400):
        title = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 25)))
        translit = rng.choice([{}, {"é": "e", "Ü": "Ue", "ß": "ss"}, {"!": "-bang-", "a": "A"}])
        max_len = rng.randint(1, 30)
        got = slugify(title, translit, max_len)
        assert got == _oracle(title, translit, max_len), (title, translit, max_len)
        assert got == "" or re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", got)
