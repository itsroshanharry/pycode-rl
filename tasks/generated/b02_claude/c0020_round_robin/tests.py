import itertools
import random
from collections import deque

import pytest
from solution import round_robin


def _norm(result):
    return [[tuple(m) for m in rnd] for rnd in result]


@pytest.mark.parametrize(
    "teams, expected",
    [
        (["A", "B", "C", "D"], [[("A", "D"), ("B", "C")], [("A", "C"), ("D", "B")], [("A", "B"), ("C", "D")]]),
        (["A", "B", "C"], [[("B", "C")], [("A", "C")], [("A", "B")]]),
        (["X", "Y"], [[("X", "Y")]]),
        (["p", "q", "r", "s", "t", "u"], [
            [("p", "u"), ("q", "t"), ("r", "s")],
            [("p", "t"), ("u", "s"), ("q", "r")],
            [("p", "s"), ("t", "r"), ("u", "q")],
            [("p", "r"), ("s", "q"), ("t", "u")],
            [("p", "q"), ("r", "u"), ("s", "t")],
        ]),
    ],
)
def test_examples(teams, expected):
    assert _norm(round_robin(teams)) == expected


@pytest.mark.parametrize("teams", [[], ["A"], ["A", "A"], ["A", "B", "A"], ["A", "BYE"]])
def test_invalid(teams):
    with pytest.raises(ValueError):
        round_robin(teams)


def _oracle(teams):
    # Same rules, using a deque rotation instead of slicing.
    entries = list(teams) + (["BYE"] if len(teams) % 2 else [])
    n = len(entries)
    ring = deque(entries[1:])
    out = []
    for _ in range(n - 1):
        arr = [entries[0]] + list(ring)
        out.append([(arr[i], arr[n - 1 - i]) for i in range(n // 2) if "BYE" not in (arr[i], arr[n - 1 - i])])
        ring.rotate(1)
    return out


@pytest.mark.parametrize("n", list(range(2, 15)))
def test_every_pair_meets_once(n):
    teams = [f"t{i}" for i in range(n)]
    rounds = _norm(round_robin(teams))
    assert rounds == _oracle(teams)
    met = [frozenset(m) for rnd in rounds for m in rnd]
    assert sorted(met, key=sorted) == sorted((frozenset(p) for p in itertools.combinations(teams, 2)), key=sorted)
    for rnd in rounds:
        playing = [t for m in rnd for t in m]
        assert len(playing) == len(set(playing))


def test_random_names():
    rng = random.Random(52)
    for _ in range(50):
        teams = rng.sample(["Ann", "Bo", "Cy", "Di", "Ed", "Flo", "Gus", "Hal"], rng.randint(2, 8))
        assert _norm(round_robin(teams)) == _oracle(teams)
