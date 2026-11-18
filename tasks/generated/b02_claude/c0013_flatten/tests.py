import random

import pytest
from solution import flatten


@pytest.mark.parametrize(
    "obj, expected",
    [
        ({"a": {"b": [10, {"c": 1}]}, "d": None}, [("a.b[0]", 10), ("a.b[1].c", 1), ("d", None)]),
        ({"x": [], "y": {}, "z": [[1]]}, [("x", []), ("y", {}), ("z[0][0]", 1)]),
        ({}, []),
        ({"a": 1}, [("a", 1)]),
        ({"a": {"b": {"c": {"d": 2}}}}, [("a.b.c.d", 2)]),
        ({"l": [1, [2, [3]]]}, [("l[0]", 1), ("l[1][0]", 2), ("l[1][1][0]", 3)]),
        ({"a": [{}]}, [("a[0]", {})]),
        ({"k": (1, 2)}, [("k", (1, 2))]),
        ({"s": "str", "f": 1.5, "t": True}, [("s", "str"), ("f", 1.5), ("t", True)]),
        ({"a b": {"c-d": 0}}, [("a b.c-d", 0)]),
        ({"z": 1, "a": {"y": 2, "b": 3}}, [("z", 1), ("a.y", 2), ("a.b", 3)]),
        ({"m": [[], [{}], {"n": []}]}, [("m[0]", []), ("m[1][0]", {}), ("m[2].n", [])]),
    ],
)
def test_flatten_order_and_values(obj, expected):
    result = flatten(obj)
    assert list(result.items()) == expected
    assert [type(v) for v in result.values()] == [type(v) for _, v in expected]


@pytest.mark.parametrize("obj", [[1], "x", None, 5])
def test_not_a_dict(obj):
    with pytest.raises(TypeError):
        flatten(obj)


@pytest.mark.parametrize("obj", [{"a.b": 1}, {"": 1}, {"a": {"x]": 1}}, {"a": [{"[": 1}]}, {1: 2}, {"a": {2: 3}}])
def test_bad_keys(obj):
    with pytest.raises(ValueError):
        flatten(obj)


def _random(rng, depth=0):
    r = rng.random()
    if depth > 3 or r < 0.3:
        return rng.choice([0, "v", None, 2.5, False])
    if r < 0.65:
        return {rng.choice("abcxyz") + str(i): _random(rng, depth + 1) for i in range(rng.randint(0, 3))}
    return [_random(rng, depth + 1) for _ in range(rng.randint(0, 3))]


def _oracle(obj):
    # Iterative depth-first walk with an explicit stack.
    out, stack = [], [(k, v) for k, v in reversed(list(obj.items()))]
    while stack:
        path, v = stack.pop()
        if isinstance(v, dict) and v:
            stack += [(f"{path}.{k}", x) for k, x in reversed(list(v.items()))]
        elif isinstance(v, list) and v:
            stack += [(f"{path}[{i}]", x) for i, x in reversed(list(enumerate(v)))]
        else:
            out.append((path, v))
    return out


def test_random_against_oracle():
    rng = random.Random(33)
    for _ in range(200):
        obj = _random(rng)
        if not isinstance(obj, dict):
            obj = {"root": obj}
        assert list(flatten(obj).items()) == _oracle(obj), obj
