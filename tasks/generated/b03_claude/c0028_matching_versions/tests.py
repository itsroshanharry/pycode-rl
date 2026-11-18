import itertools
import random

import pytest
from solution import matching_versions

POOL = [f"{a}.{b}.{c}" for a, b, c in itertools.product(range(3), range(3), range(3))]


@pytest.mark.parametrize(
    "versions, spec, expected",
    [
        (["1.2.0", "1.2.9", "1.3.0", "2.0.0"], "<=1.2 || >=2", ["1.2.0", "1.2.9", "2.0.0"]),
        (["0.9.9", "1.0.0", "1.5.1"], ">=1 <1.5", ["1.0.0"]),
        (["1.2.3", "1.2.4"], "1.2.3", ["1.2.3"]),
        (["1.2.3", "1.3.0", "2.0.0"], "=1", ["1.2.3", "1.3.0"]),
        (["1.2.0", "1.2.7", "1.3.0"], ">1.2", ["1.3.0"]),
        (["1.1.9", "1.2.0"], "<1.2", ["1.1.9"]),
        (["1.2.3", "1.2.4", "1.2.2"], ">1.2.3", ["1.2.4"]),
        (["1.2.3", "1.2.4"], "<=1.2.3", ["1.2.3"]),
        (["0.0.1", "5.6.7"], "*", ["0.0.1", "5.6.7"]),
        (["1.0.0", "3.0.0"], "* || >5", ["1.0.0", "3.0.0"]),
        ([], ">=0", []),
        (["2.0.0", "1.0.0", "2.0.0"], "2", ["2.0.0", "2.0.0"]),
        (["1.0.0", "2.5.0", "3.0.0"], " >=2   <3 ||1.0.0 ", ["1.0.0", "2.5.0"]),
        (["10.0.0", "9.0.0"], ">9", ["10.0.0"]),
        (["1.2.3"], ">=1.2.4 <1.2.3", []),
    ],
)
def test_examples(versions, spec, expected):
    assert list(matching_versions(versions, spec)) == expected


@pytest.mark.parametrize("spec", ["", "||", ">=1 ||", "|| >=1", ">= 1", "~1.2", "^1", "=>1", "1.2.3.4", "01.2", "1.02", ">=1.x", "**", "* >1", "a"])
def test_bad_range(spec):
    with pytest.raises(ValueError):
        matching_versions(["1.0.0"], spec)


@pytest.mark.parametrize("version", ["1.0", "1.0.0.0", "01.0.0", "1.0.0-beta", " 1.0.0", "v1.0.0"])
def test_bad_version(version):
    with pytest.raises(ValueError):
        matching_versions([version], "*")


def _bounds(op, parts):
    # Independent: translate each comparator into a half-open interval [lo, hi) of full versions.
    p = list(parts)
    lo_eq = tuple(p + [0] * (3 - len(p)))
    nxt = p[:-1] + [p[-1] + 1]
    hi_eq = tuple(nxt + [0] * (3 - len(nxt)))  # first version past the partial range
    inf = (10**9, 0, 0)
    return {"=": (lo_eq, hi_eq), ">": (hi_eq, inf), ">=": (lo_eq, inf), "<": ((0, 0, 0), lo_eq), "<=": ((0, 0, 0), hi_eq)}[op]


def _oracle(versions, alts):
    out = []
    for v in versions:
        t = tuple(int(x) for x in v.split("."))
        if any(all(lo <= t < hi for lo, hi in (_bounds(op, parts) for op, parts in alt)) for alt in alts):
            out.append(v)
    return out


def test_random_against_intervals():
    rng = random.Random(12)
    ops = ["", "=", ">", ">=", "<", "<="]
    for _ in range(300):
        alts, text_alts = [], []
        for _ in range(rng.randint(1, 3)):
            comps, texts = [], []
            for _ in range(rng.randint(1, 2)):
                op = rng.choice(ops)
                parts = tuple(rng.randint(0, 2) for _ in range(rng.randint(1, 3)))
                comps.append((op or "=", parts))
                texts.append(op + ".".join(map(str, parts)))
            alts.append(comps)
            text_alts.append(" ".join(texts))
        spec = rng.choice([" || ", "||", "  ||  "]).join(text_alts)
        versions = rng.sample(POOL, rng.randint(0, 10))
        assert list(matching_versions(versions, spec)) == _oracle(versions, alts), spec
