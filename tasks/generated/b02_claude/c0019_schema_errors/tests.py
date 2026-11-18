import random

import pytest
from solution import schema_errors

USER = {
    "type": "dict",
    "fields": {
        "age": {"type": "int", "min": 0},
        "tags": {"type": "list", "items": {"type": "str"}},
        "name": {"type": "str"},
    },
    "required": ["name"],
}


@pytest.mark.parametrize(
    "value, schema, expected",
    [
        ({"age": -1, "tags": ["a", 3]}, USER, ["$.age: below min 0", "$.tags[1]: expected str", "$.name: missing required field"]),
        ({"name": "x"}, USER, []),
        ({"name": "x", "extra": [1, {}]}, USER, []),
        (5, {"type": "int"}, []),
        (True, {"type": "int"}, ["$: expected int"]),
        (True, {"type": "float"}, ["$: expected float"]),
        (3, {"type": "float", "max": 2.5}, ["$: above max 2.5"]),
        (2.5, {"type": "float", "min": 0, "max": 2.5}, []),
        (1, {"type": "bool"}, ["$: expected bool"]),
        (None, {"type": "null"}, []),
        (0, {"type": "null"}, ["$: expected null"]),
        ("abcd", {"type": "str", "max_len": 3}, ["$: longer than 3"]),
        ("abc", {"type": "str", "max_len": 3}, []),
        ((1, 2), {"type": "list"}, ["$: expected list"]),
        ([], {"type": "list", "items": {"type": "int"}}, []),
        ([1, "x", 2, None], {"type": "list", "items": {"type": "int"}}, ["$[1]: expected int", "$[3]: expected int"]),
        ("not a dict", USER, ["$: expected dict"]),
        ({"age": "old", "name": 5}, USER, ["$.age: expected int", "$.name: expected str"]),
        ({}, {"type": "dict", "required": ["b", "a"]}, ["$.b: missing required field", "$.a: missing required field"]),
        (7, {"type": "int", "min": 10, "max": 5}, ["$: below min 10", "$: above max 5"]),
        ({"m": [[{"v": 11}]]}, {"type": "dict", "fields": {"m": {"type": "list", "items": {"type": "list", "items": {"type": "dict", "fields": {"v": {"type": "int", "max": 10}}, "required": ["w"]}}}}},
         ["$.m[0][0].v: above max 10", "$.m[0][0].w: missing required field"]),
        ({"b": 1, "a": "x"}, {"type": "dict", "fields": {"a": {"type": "int"}, "b": {"type": "str"}}}, ["$.a: expected int", "$.b: expected str"]),
        ({"t": True}, {"type": "dict", "fields": {"t": {"type": "bool"}}, "required": ["t"]}, []),
    ],
)
def test_errors(value, schema, expected):
    assert list(schema_errors(value, schema)) == expected


def _random_schema(rng, depth=0):
    t = rng.choice(["int", "float", "str", "bool", "null"] + (["list", "dict"] if depth < 3 else []))
    s = {"type": t}
    if t in ("int", "float") and rng.random() < 0.5:
        s["min"], s["max"] = -5, 5
    if t == "str" and rng.random() < 0.5:
        s["max_len"] = 4
    if t == "list":
        s["items"] = _random_schema(rng, depth + 1)
    if t == "dict":
        s["fields"] = {f"f{i}": _random_schema(rng, depth + 1) for i in range(rng.randint(0, 3))}
        s["required"] = [k for k in s["fields"] if rng.random() < 0.5]
    return s


def _valid_instance(rng, s):
    t = s["type"]
    if t == "int":
        return rng.randint(-5, 5)
    if t == "float":
        return rng.choice([rng.randint(-5, 5), rng.uniform(-5, 5)])
    if t == "str":
        return "ab"[: rng.randint(0, 2)]
    if t == "bool":
        return rng.random() < 0.5
    if t == "null":
        return None
    if t == "list":
        return [_valid_instance(rng, s["items"]) for _ in range(rng.randint(0, 3))]
    return {k: _valid_instance(rng, sub) for k, sub in s["fields"].items() if k in s["required"] or rng.random() < 0.5}


def test_random_valid_instances_have_no_errors():
    rng = random.Random(35)
    for _ in range(200):
        schema = _random_schema(rng)
        value = _valid_instance(rng, schema)
        assert list(schema_errors(value, schema)) == [], (value, schema)
