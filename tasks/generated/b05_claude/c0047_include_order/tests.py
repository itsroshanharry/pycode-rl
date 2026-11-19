import random

import pytest
from solution import include_order


@pytest.mark.parametrize(
    "files, root, expected",
    [
        ({"app": ["db", "log"], "db": ["log"], "log": []}, "app", ["log", "db", "app"]),
        ({"a": []}, "a", ["a"]),
        ({"a": ["b", "c"], "b": [], "c": []}, "a", ["b", "c", "a"]),
        ({"a": ["c", "b"], "b": [], "c": []}, "a", ["c", "b", "a"]),
        ({"a": ["b", "b"], "b": []}, "a", ["b", "a"]),
        ({"a": ["b"], "b": [], "unused": ["missing"]}, "a", ["b", "a"]),
        ({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}, "a", ["d", "b", "c", "a"]),
        ({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}, "c", ["d", "c"]),
        ({"r": ["x", "y"], "x": ["z"], "y": ["x", "z"], "z": []}, "r", ["z", "x", "y", "r"]),
    ],
)
def test_examples(files, root, expected):
    assert list(include_order(files, root)) == expected


@pytest.mark.parametrize(
    "files, root, message",
    [
        ({"a": ["a"]}, "a", "include cycle: a -> a"),
        ({"a": ["b"], "b": ["a"]}, "a", "include cycle: a -> b -> a"),
        ({"a": ["b"], "b": ["c"], "c": ["b"]}, "a", "include cycle: b -> c -> b"),
        ({"r": ["ok", "p"], "ok": [], "p": ["q"], "q": ["s"], "s": ["p"]}, "r", "include cycle: p -> q -> s -> p"),
        ({"a": ["b", "c"], "b": [], "c": ["b", "d"], "d": ["c"]}, "a", "include cycle: c -> d -> c"),
        ({"a": ["b"]}, "a", "missing file: b"),
        ({"a": []}, "zzz", "missing file: zzz"),
        ({"a": ["b", "gone"], "b": []}, "a", "missing file: gone"),
        # depth-first: the cycle under "x" is reached before the missing file
        ({"a": ["x", "gone"], "x": ["x"]}, "a", "include cycle: x -> x"),
    ],
)
def test_errors(files, root, message):
    with pytest.raises(ValueError) as info:
        include_order(files, root)
    assert str(info.value) == message


def test_deep_chain():
    n = 5000
    files = {f"f{i}": [f"f{i + 1}"] for i in range(n)}
    files[f"f{n}"] = []
    assert list(include_order(files, "f0")) == [f"f{i}" for i in range(n, -1, -1)]


def test_deep_cycle():
    n = 3000
    files = {f"f{i}": [f"f{i + 1}"] for i in range(n)}
    files[f"f{n}"] = ["f2998"]
    with pytest.raises(ValueError) as info:
        include_order(files, "f0")
    assert str(info.value) == "include cycle: f2998 -> f2999 -> f3000 -> f2998"


def _oracle(files, root):
    out, placed = [], set()

    def visit(name, path):
        for child in files[name]:
            if child not in placed:
                visit(child, path + [child])
        placed.add(name)
        out.append(name)

    visit(root, [root])
    return out


def test_random_dags_against_oracle():
    rng = random.Random(37)
    for _ in range(200):
        n = rng.randint(1, 12)
        names = [f"n{i}" for i in range(n)]
        # edges only point to higher indices, so there are no cycles
        files = {names[i]: rng.sample(names[i + 1:], rng.randint(0, min(3, n - i - 1))) for i in range(n)}
        root = names[rng.randrange(n)]
        assert list(include_order(files, root)) == _oracle(files, root)
