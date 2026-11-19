import random

import pytest
from solution import deep_merge


@pytest.mark.parametrize(
    "base, override, policy, expected",
    [
        ({"db": {"host": "a", "port": 1}, "tags": [1]}, {"db": {"port": None}, "tags": [2]}, "error", {"db": {"host": "a"}, "tags": [2]}),
        ({}, {}, "error", {}),
        ({"a": 1}, {}, "error", {"a": 1}),
        ({}, {"a": 1}, "error", {"a": 1}),
        ({"a": 1}, {"a": None}, "error", {}),
        ({"a": 1}, {"b": None}, "error", {"a": 1}),
        ({"a": None}, {}, "error", {"a": None}),
        ({"a": None}, {"a": 2}, "error", {"a": 2}),
        ({"a": [1, 2]}, {"a": [3]}, "error", {"a": [3]}),
        ({"a": [1, 2]}, {"a": []}, "error", {"a": []}),
        ({"a": 1}, {"a": [None, 2]}, "error", {"a": [None, 2]}),
        ({}, {"a": {"b": None, "c": {"d": None, "e": 1}}}, "error", {"a": {"c": {"e": 1}}}),
        ({"a": {"x": 1}}, {"a": {"b": {"c": None}}}, "error", {"a": {"x": 1, "b": {}}}),
        ({"a": {"b": {"c": 1, "d": 2}}}, {"a": {"b": {"c": 9}}}, "error", {"a": {"b": {"c": 9, "d": 2}}}),
        ({"a": 1, "b": 2}, {"c": 3, "a": 4}, "error", {"a": 4, "b": 2, "c": 3}),
        ({"a": "x"}, {"a": 5}, "error", {"a": 5}),
        ({"a": [1]}, {"a": "s"}, "error", {"a": "s"}),
        ({"a": True}, {"a": False}, "error", {"a": False}),
        ({"a": {"b": 1}}, {"a": 5}, "override", {"a": 5}),
        ({"a": {"b": 1}}, {"a": 5}, "keep", {"a": {"b": 1}}),
        ({"a": 5}, {"a": {"b": 1, "c": None}}, "override", {"a": {"b": 1}}),
        ({"a": 5}, {"a": {"b": 1}}, "keep", {"a": 5}),
        ({"a": [1]}, {"a": {"b": 1}}, "keep", {"a": [1]}),
        ({"a": {"b": 1}}, {"a": [1]}, "override", {"a": [1]}),
        ({"a": {}}, {"a": {}}, "error", {"a": {}}),
        ({"a": {"b": 1}}, {"a": None}, "error", {}),
        ({"a": {"b": 1}, "z": 0}, {"a": {"b": None}}, "error", {"a": {}, "z": 0}),
    ],
)
def test_examples(base, override, policy, expected):
    got = deep_merge(base, override, policy)
    assert got == expected
    assert list(got) == list(expected)


@pytest.mark.parametrize(
    "base, override, message",
    [
        ({"a": {"b": 1}}, {"a": 5}, "conflict at a"),
        ({"db": {"port": 1}}, {"db": {"port": {"n": 1}}}, "conflict at db.port"),
        ({"x": {"y": {"z": [1]}}}, {"x": {"y": {"z": {"w": 1}}}}, "conflict at x.y.z"),
        ({"a": 1}, {"a": {}}, "conflict at a"),
    ],
)
def test_conflict_error(base, override, message):
    with pytest.raises(ValueError) as info:
        deep_merge(base, override, "error")
    assert str(info.value) == message


def test_unknown_policy():
    with pytest.raises(ValueError):
        deep_merge({}, {}, "merge")


def _clean(v):
    return {k: _clean(x) for k, x in v.items() if x is not None} if isinstance(v, dict) else v


def _oracle(b, o, policy):
    res = dict(b)
    for k, v in o.items():
        if v is None:
            res.pop(k, None)
        elif k not in res:
            res[k] = _clean(v)
        elif isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = _oracle(res[k], v, policy)
        elif isinstance(res[k], dict) or isinstance(v, dict):
            if policy == "override":
                res[k] = _clean(v)
        else:
            res[k] = v
    return res


def _rand_value(rng, depth):
    r = rng.random()
    if depth < 3 and r < 0.35:
        return {rng.choice("abc"): _rand_value(rng, depth + 1) for _ in range(rng.randint(0, 3))}
    if r < 0.5:
        return None
    if r < 0.65:
        return [rng.randint(0, 3) for _ in range(rng.randint(0, 2))]
    return rng.randint(0, 9)


def test_random_against_oracle():
    rng = random.Random(32)
    for _ in range(400):
        base = {rng.choice("abcd"): _rand_value(rng, 1) for _ in range(rng.randint(0, 4))}
        over = {rng.choice("abcd"): _rand_value(rng, 1) for _ in range(rng.randint(0, 4))}
        policy = rng.choice(["override", "keep"])
        assert deep_merge(base, over, policy) == _oracle(base, over, policy), (base, over, policy)
