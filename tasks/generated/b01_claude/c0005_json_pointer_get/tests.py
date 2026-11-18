import random

import pytest
from solution import json_pointer_get

DOC = {"a": {"b/c": [10, 20], "": {"": 3}, "m~n": 8}, "~1": 5, "/": 6, "0": "zero", " ": 7,
       "list": [1, [2, 3], {"k": None}], "s": "text", "n": 4}


@pytest.mark.parametrize(
    "doc, pointer, expected",
    [
        ({"a": {"b/c": [10, 20]}}, "/a/b~1c/1", 20),
        ({"": 1}, "/", 1),
        (DOC, "", DOC),
        (DOC, "/n", 4),
        (DOC, "/a/m~0n", 8),
        (DOC, "/~01", 5),
        (DOC, "/~1", 6),
        (DOC, "/0", "zero"),
        (DOC, "/ ", 7),
        (DOC, "/a//", 3),
        (DOC, "/list/1/0", 2),
        (DOC, "/list/2/k", None),
        (DOC, "/list/2", {"k": None}),
        ([[], [[7]]], "/1/0/0", 7),
        (5, "", 5),
    ],
)
def test_lookup(doc, pointer, expected):
    assert json_pointer_get(doc, pointer) == expected


@pytest.mark.parametrize("pointer", ["a", "a/b", "/~", "/x~2", "/a~", "/n/~"])
def test_syntax_errors(pointer):
    with pytest.raises(ValueError):
        json_pointer_get(DOC, pointer)


def test_escape_checked_before_lookup():
    with pytest.raises(ValueError):
        json_pointer_get(DOC, "/missing/~2")


@pytest.mark.parametrize("pointer", ["/missing", "/a/x", "/a/b~0c"])
def test_missing_key(pointer):
    with pytest.raises(KeyError):
        json_pointer_get(DOC, pointer)


@pytest.mark.parametrize("pointer", ["/list/3", "/list/-", "/list/01", "/list/-1", "/list/1.0", "/list/ 1", "/list/"])
def test_bad_index(pointer):
    with pytest.raises(IndexError):
        json_pointer_get(DOC, pointer)


@pytest.mark.parametrize("pointer", ["/n/x", "/s/0", "/list/0/0"])
def test_scalar(pointer):
    with pytest.raises(TypeError):
        json_pointer_get(DOC, pointer)


def _random_doc(rng, depth=0):
    if depth > 3 or rng.random() < 0.3:
        return rng.choice([0, 1, "x", None, True, 2.5])
    if rng.random() < 0.5:
        return [_random_doc(rng, depth + 1) for _ in range(rng.randint(0, 3))]
    keys = ["a", "", "~", "/", "~1", "0", "a/b", "x~y"]
    return {k: _random_doc(rng, depth + 1) for k in rng.sample(keys, rng.randint(0, 4))}


def _paths(doc, prefix=""):
    # Independent walk: encode keys ("~" -> "~0" first, then "/" -> "~1").
    yield prefix, doc
    if isinstance(doc, dict):
        for k, v in doc.items():
            yield from _paths(v, prefix + "/" + k.replace("~", "~0").replace("/", "~1"))
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            yield from _paths(v, f"{prefix}/{i}")


def test_random_all_paths():
    rng = random.Random(31)
    for _ in range(120):
        doc = _random_doc(rng)
        for pointer, value in _paths(doc):
            assert json_pointer_get(doc, pointer) == value, (doc, pointer)
