import random

import pytest
from solution import rollout_bucket


def _fnv(s):
    h = 2166136261
    for b in s.encode("utf-8"):
        h = ((h ^ b) * 16777619) % 4294967296
    return h


def test_fnv_reference_vectors_via_oracle():
    # published FNV-1a 32-bit test vectors, checking the test's own oracle
    assert _fnv("") == 0x811C9DC5
    assert _fnv("a") == 0xE40C292C
    assert _fnv("foobar") == 0xBF9CF968


@pytest.mark.parametrize(
    "flag, user",
    [("new-ui", "user-42"), ("", ""), ("checkout", "17"), ("dark-mode", "élodie"), ("flag", "用户"), ("a:b", "c"), ("x", "😀")],
)
def test_bucket_matches_fnv1a(flag, user):
    bucket, _ = rollout_bucket(flag, user, "50")
    assert bucket == _fnv(f"{flag}:{user}") % 10000


@pytest.mark.parametrize("percent, bp", [
    ("0", 0), ("100", 10000), ("100.00", 10000), ("100.0", 10000), ("12.5", 1250), ("12.50", 1250), ("0.01", 1),
    ("05", 500), ("99.99", 9999), ("7", 700), ("33.3", 3330),
])
def test_threshold(percent, bp):
    rng = random.Random(percent)
    for _ in range(300):
        user = str(rng.randrange(10 ** 9))
        bucket, included = rollout_bucket("exp", user, percent)
        assert included is (bucket < bp)


def test_exact_boundary():
    # find users whose bucket is exactly 1250 / 1249 and check the strict "<"
    found = {}
    for i in range(200000):
        b = _fnv(f"exp:{i}") % 10000
        if b in (1249, 1250) and b not in found:
            found[b] = str(i)
        if len(found) == 2:
            break
    assert rollout_bucket("exp", found[1249], "12.5") == (1249, True)
    assert rollout_bucket("exp", found[1250], "12.5") == (1250, False)
    assert rollout_bucket("exp", found[1250], "12.51") == (1250, True)


@pytest.mark.parametrize("percent", ["", "-1", "101", "100.01", "100.5", "1000", "12.555", "12.", ".5", " 5", "5 ", "+5", "5%", "５", "1e1", "005"])
def test_invalid(percent):
    with pytest.raises(ValueError):
        rollout_bucket("f", "u", percent)
