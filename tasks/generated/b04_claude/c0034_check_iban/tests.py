import random
import string

import pytest
from solution import check_iban

L = {"GB": 22, "DE": 22, "NO": 15, "FR": 27}


@pytest.mark.parametrize(
    "iban, expected",
    [
        ("GB82 WEST 1234 5698 7654 32", "ok"),
        ("GB82WEST12345698765432", "ok"),
        ("DE89 3704 0044 0532 0130 00", "ok"),
        ("NO93 8601 1117 947", "ok"),
        ("FR14 2004 1010 0505 0001 3M02 606", "ok"),
        ("GB82 WEST 1234 5698 7654 33", "checksum"),
        ("GB28 WEST 1234 5698 7654 32", "checksum"),
        ("GB82 WEST 1234 5698 7654 3", "length"),
        ("GB82 WEST 1234 5698 7654 321", "length"),
        ("XX82 WEST 1234 5698 7654 32", "country"),
        ("gb82 WEST 1234 5698 7654 32", "format"),
        ("GB82 west 1234 5698 7654 32", "format"),
        ("GB82-WEST-1234-5698-7654-32", "format"),
        ("GBX2 WEST 1234 5698 7654 32", "format"),
        ("1B82 WEST 1234 5698 7654 32", "format"),
        ("", "format"),
        ("GB8", "format"),
        ("GB82", "length"),
        ("GB82\tWEST12345698765432", "format"),
        ("  NO93 8601 1117 947  ", "ok"),
        ("XX00", "country"),
    ],
)
def test_examples(iban, expected):
    assert check_iban(iban, L) == expected


def _make(country, length, rng):
    body = "".join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(length - 4))
    num = "".join(str(ord(c) - 55) if c.isalpha() else c for c in body + country + "00")
    check = 98 - int(num) % 97  # standard way to compute the two check digits
    return f"{country}{check:02d}{body}"


def _mod97(s):
    # Piecewise remainder (independent of big-int conversion).
    r = 0
    for ch in s[4:] + s[:4]:
        for d in (str(ord(ch) - 55) if ch.isalpha() else ch):
            r = (r * 10 + int(d)) % 97
    return r


def test_random_valid_and_corrupted():
    rng = random.Random(13)
    for _ in range(200):
        country = rng.choice(list(L))
        iban = _make(country, L[country], rng)
        assert check_iban(iban, L) == "ok", iban
        spaced = " ".join(iban[i : i + 4] for i in range(0, len(iban), 4))
        assert check_iban(spaced, L) == "ok", spaced
        i = rng.randrange(4, len(iban))
        other = rng.choice([c for c in string.digits if c != iban[i]]) if iban[i].isdigit() else rng.choice([c for c in string.ascii_uppercase if c != iban[i]])
        bad = iban[:i] + other + iban[i + 1 :]
        assert check_iban(bad, L) == ("ok" if _mod97(bad) == 1 else "checksum"), bad
