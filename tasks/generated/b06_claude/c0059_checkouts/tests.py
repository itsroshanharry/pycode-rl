import itertools

import pytest
from solution import checkouts

# Counts below were computed independently by brute force over all ordered dart sequences.
@pytest.mark.parametrize(
    "score, expected",
    [
        (170, (1, ["T20", "T20", "DB"])),
        (11, (36, ["T3", "D1"])),
        (2, (1, ["D1"])),
        (3, (1, ["S1", "D1"])),
        (4, (4, ["D2"])),
        (5, (5, ["T1", "D1"])),
        (6, (11, ["D3"])),
        (40, (541, ["D20"])),
        (41, (456, ["T13", "D1"])),
        (50, (687, ["DB"])),
        (100, (281, ["T20", "D20"])),
        (160, (2, ["T20", "T20", "D20"])),
        (167, (1, ["T20", "T19", "DB"])),
        (158, (4, ["T20", "T20", "D19"])),
        (169, (0, None)),
        (171, (0, None)),
        (1, (0, None)),
        (0, (0, None)),
        (-5, (0, None)),
        (1000, (0, None)),
    ],
)
def test_examples(score, expected):
    count, best = checkouts(score)
    assert (count, None if best is None else list(best)) == expected


_DARTS = [(f"S{i}", i, 0) for i in range(1, 21)] + [("SB", 25, 0)] + [(f"D{i}", 2 * i, 1) for i in range(1, 21)] + [
    ("DB", 50, 1)] + [(f"T{i}", 3 * i, 2) for i in range(1, 21)]
_INFO = {n: (v, r) for n, v, r in _DARTS}


def _oracle(score):
    seen = set()
    doubles = [d for d in _DARTS if d[0][0] == "D"]
    for k in (0, 1, 2):
        for pre in itertools.product(_DARTS, repeat=k):
            for f in doubles:
                if sum(d[1] for d in pre) + f[1] == score:
                    seen.add((tuple(sorted(d[0] for d in pre)), f[0]))
    if not seen:
        return 0, None
    ranked = sorted(seen, key=lambda c: (len(c[0]), sorted((tuple(-x for x in _INFO[n]) for n in c[0]))))
    e, f = ranked[0]
    return len(seen), sorted(e, key=lambda n: _INFO[n], reverse=True) + [f]


@pytest.mark.parametrize("score", [7, 22, 37, 52, 61, 75, 99, 101, 110, 121, 132, 141, 150, 161, 164])
def test_against_brute_force(score):
    count, best = checkouts(score)
    assert (count, None if best is None else list(best)) == _oracle(score)
