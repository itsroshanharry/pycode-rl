import random

import pytest
from solution import exam_slots

DOC = {"math": ["ann", "bob"], "art": ["bob"], "bio": ["cat"], "chem": ["ann", "cat"]}


def _oracle(exams, slots, per_slot):
    # independent: pairwise set intersection for conflicts
    st = {e: set(v) for e, v in exams.items()}
    conf = {e: {f for f in exams if f != e and st[e] & st[f]} for e in exams}
    order = sorted(exams, key=lambda e: (-len(conf[e]), -len(st[e]), e))
    where, count = {}, {}
    for e in order:
        for t in range(slots):
            if count.get(t, 0) < per_slot and all(where.get(f) != t for f in conf[e]):
                where[e] = t
                count[t] = count.get(t, 0) + 1
                break
        else:
            raise ValueError(e)
    return dict(sorted(where.items()))


CASES = [
    (DOC, 3, 2),
    ({}, 1, 1),
    ({"a": []}, 1, 1),
    ({"a": ["s"], "b": ["s"], "c": ["s"]}, 3, 1),
    ({"a": ["s", "s", "s"], "b": ["t"]}, 1, 2),
    ({"x": ["1", "2", "3"], "y": ["1"], "z": ["2"], "w": ["9"]}, 2, 3),
    ({"p": ["a", "b"], "q": ["a", "b"], "r": ["c"]}, 2, 2),
    ({"e1": ["s1", "s2"], "e2": ["s1"], "e3": ["s2"], "e4": ["s3", "s4", "s5"]}, 3, 2),
    ({"m": ["a"], "n": ["b"], "o": ["c"], "p": ["d"]}, 2, 2),
    ({"B": ["x"], "a": ["x"], "b": ["y"]}, 2, 2),
]

# Literal results produced by _oracle (not by hand).
FIXED = [
    (CASES[0], {"art": 0, "bio": 1, "chem": 0, "math": 1}),
    (CASES[3], {"a": 0, "b": 1, "c": 2}),
    (CASES[8], {"m": 0, "n": 0, "o": 1, "p": 1}),
]


@pytest.mark.parametrize("args", CASES)
def test_against_oracle(args):
    got = exam_slots(*args)
    assert got == _oracle(*args)
    assert list(got) == sorted(args[0])


@pytest.mark.parametrize("args, expected", FIXED)
def test_fixed(args, expected):
    assert exam_slots(*args) == expected


@pytest.mark.parametrize(
    "args",
    [(DOC, 0, 1), (DOC, 1, 0), ({}, 0, 1), ({}, 1, 0), ({}, -3, 2),({"a": ["s"], "b": ["s"]}, 1, 5), ({"a": [], "b": [], "c": []}, 1, 2),
     ({"a": ["s"], "b": ["s"], "c": ["s"]}, 2, 9), ({"p": ["a", "b"], "q": ["a", "b"], "r": ["c"]}, 2, 1)],
)
def test_invalid(args):
    with pytest.raises(ValueError):
        exam_slots(*args)


def test_random_against_oracle():
    rng = random.Random(58)
    for _ in range(400):
        exams = {f"e{i}": [rng.choice("abcdefgh") for _ in range(rng.randint(0, 4))] for i in range(rng.randint(0, 8))}
        args = (exams, rng.randint(1, 5), rng.randint(1, 4))
        try:
            want = _oracle(*args)
        except ValueError:
            with pytest.raises(ValueError):
                exam_slots(*args)
            continue
        assert exam_slots(*args) == want, args
