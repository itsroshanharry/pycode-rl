import functools
import random

import pytest
from solution import semver_sort


@pytest.mark.parametrize(
    "versions, expected",
    [
        (["1.0.0", "1.0.0-alpha", "0.9.12"], ["0.9.12", "1.0.0-alpha", "1.0.0"]),
        (["1.0.0-alpha.beta", "1.0.0-alpha.1", "1.0.0-alpha"], ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta"]),
        ([], []),
        (["10.0.0", "9.0.0", "2.10.0", "2.9.0"], ["2.9.0", "2.10.0", "9.0.0", "10.0.0"]),
        (["1.0.0-rc.1", "1.0.0", "1.0.0-beta.11", "1.0.0-alpha", "1.0.0-beta.2", "1.0.0-beta", "1.0.0-alpha.beta", "1.0.0-alpha.1"],
         ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]),
        (["1.0.0+b", "1.0.0+a", "1.0.0"], ["1.0.0+b", "1.0.0+a", "1.0.0"]),
        (["1.0.0-a+x", "1.0.0-a", "0.0.1"], ["0.0.1", "1.0.0-a+x", "1.0.0-a"]),
        (["1.0.0-b", "1.0.0-B", "1.0.0-a"], ["1.0.0-B", "1.0.0-a", "1.0.0-b"]),
        (["1.0.0-alpha", "1.0.0-1"], ["1.0.0-1", "1.0.0-alpha"]),
        (["1.0.0-rc.10", "1.0.0-rc.2"], ["1.0.0-rc.2", "1.0.0-rc.10"]),
        (["1.0.0-0a", "1.0.0-1"], ["1.0.0-1", "1.0.0-0a"]),
        (["1.0.0-x-y", "1.0.0-x"], ["1.0.0-x", "1.0.0-x-y"]),
        (["2.0.0", "1.99.99", "1.99.99-zzz"], ["1.99.99-zzz", "1.99.99", "2.0.0"]),
        (["0.0.0", "0.0.0+001", "0.0.0-0"], ["0.0.0-0", "0.0.0", "0.0.0+001"]),
    ],
)
def test_order(versions, expected):
    assert list(semver_sort(versions)) == expected


@pytest.mark.parametrize(
    "bad",
    ["1.0", "1.0.0.0", "01.0.0", "1.01.0", "1.0.0-", "1.0.0+", "1.0.0-01", "1.0.0-alpha..1",
     "v1.0.0", " 1.0.0", "1.0.0-al_pha", "1.0.0+b..c", "-1.0.0", "1.0.0-alpha.", ""],
)
def test_invalid(bad):
    with pytest.raises(ValueError):
        semver_sort(["1.0.0", bad])


def _cmp(a, b):
    # Independent pairwise comparator written directly from the rules.
    def split(v):
        core, _, _ = v.partition("+")
        core, _, pre = core.partition("-")
        return [int(x) for x in core.split(".")], (pre.split(".") if pre else None)

    (ca, pa), (cb, pb) = split(a), split(b)
    if ca != cb:
        return -1 if ca < cb else 1
    if pa is None or pb is None:
        return 0 if pa is pb else (1 if pa is None else -1)
    for x, y in zip(pa, pb):
        if x == y:
            continue
        if x.isdigit() and y.isdigit():
            return -1 if int(x) < int(y) else 1
        if x.isdigit() != y.isdigit():
            return -1 if x.isdigit() else 1
        return -1 if x < y else 1
    return (len(pa) > len(pb)) - (len(pa) < len(pb))


def test_random_against_comparator():
    rng = random.Random(11)
    idents = ["alpha", "beta", "rc", "1", "2", "10", "a-b", "0a", "Z"]
    for _ in range(150):
        vs = []
        for _ in range(rng.randint(0, 7)):
            v = ".".join(str(rng.randint(0, 3)) for _ in range(3))
            if rng.random() < 0.6:
                v += "-" + ".".join(rng.choice(idents) for _ in range(rng.randint(1, 3)))
            if rng.random() < 0.3:
                v += "+" + rng.choice(["b1", "001", "x.y"])
            vs.append(v)
        expected = sorted(vs, key=functools.cmp_to_key(_cmp))  # sorted() is stable
        assert list(semver_sort(vs)) == expected, vs
