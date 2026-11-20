import random

import pytest
from solution import build_waves


def _oracle(deps, k, prio):
    # independent: explicit in-degree bookkeeping per wave
    nodes = set(deps) | {d for ds in deps.values() for d in ds}
    need = {n: set(deps.get(n, [])) for n in nodes}
    done, out = set(), []
    while done != nodes:
        ready = sorted((n for n in nodes - done if not (need[n] - done)), key=lambda n: (-prio.get(n, 0), n))
        if not ready:
            raise ValueError
        wave = ready[:k]
        out.append(sorted(wave))
        done |= set(wave)
    return out


CASES = [
    ({"app": ["lib", "cfg"], "lib": ["base"], "cfg": []}, 2, {"cfg": 5}),
    ({"a": [], "b": [], "c": []}, 2, {"c": 1}),
    ({}, 3, {}),
    ({"x": ["y"]}, 1, {}),
    ({"x": ["y", "y", "y"]}, 5, {}),
    ({"c": [], "b": [], "a": []}, 2, {}),
    ({"c": [], "b": [], "a": []}, 1, {"a": 0, "b": 0, "c": 0}),
    ({"a": [], "b": [], "c": []}, 2, {"a": -1}),
    ({"a": ["b"], "b": ["c"], "c": []}, 10, {}),
    ({"top": ["m1", "m2", "m3"], "m1": ["base"], "m2": ["base"], "m3": []}, 2, {"m3": 9, "base": -5}),
    ({"t": ["a", "b", "c", "d"]}, 2, {"d": 3, "c": 3}),
    ({"z": ["a"], "y": ["a"], "a": []}, 1, {"z": 1}),
    ({"b": [], "a": ["b"], "c": ["a", "b"]}, 1, {"c": 100, "b": -100}),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], [["base", "cfg"], ["lib"], ["app"]]),
    (CASES[1], [["a", "c"], ["b"]]),
    (CASES[7], [["b", "c"], ["a"]]),
    (CASES[9], [["base", "m3"], ["m1", "m2"], ["top"]]),
]


@pytest.mark.parametrize("deps, k, prio", CASES)
def test_against_oracle(deps, k, prio):
    assert [list(w) for w in build_waves(deps, k, prio)] == _oracle(deps, k, prio)


@pytest.mark.parametrize("args, expected", FIXED)
def test_fixed(args, expected):
    assert [list(w) for w in build_waves(*args)] == expected


@pytest.mark.parametrize(
    "deps, k",
    [({"a": []}, 0), ({"a": []}, -1), ({"a": ["a"]}, 1), ({"a": ["b"], "b": ["a"]}, 3), ({"a": ["b"], "b": ["c"], "c": ["a"], "d": []}, 2),
     ({"ok": [], "x": ["y"], "y": ["z"], "z": ["y"]}, 5)],
)
def test_invalid(deps, k):
    with pytest.raises(ValueError):
        build_waves(deps, k, {})


def test_random_dags_against_oracle():
    rng = random.Random(60)
    for _ in range(300):
        n = rng.randint(1, 10)
        names = [f"t{i}" for i in range(n)]
        deps = {}
        for i, name in enumerate(names):
            if rng.random() < 0.8:
                deps[name] = rng.sample(names[i + 1:], rng.randint(0, min(3, n - i - 1)))
        prio = {name: rng.randint(-2, 2) for name in names if rng.random() < 0.5}
        k = rng.randint(1, 4)
        assert [list(w) for w in build_waves(deps, k, prio)] == _oracle(deps, k, prio), (deps, k, prio)
