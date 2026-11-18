import random

import pytest
from solution import sessionize


def _norm(result):
    return [tuple(s) for s in result]


@pytest.mark.parametrize(
    "events, gap, expected",
    [
        ([("a", 10), ("b", 5), ("a", 100), ("a", 40)], 30, [("b", 5, 5, 1), ("a", 10, 40, 2), ("a", 100, 100, 1)]),
        ([], 10, []),
        ([("u", 7)], 0, [("u", 7, 7, 1)]),
        ([("u", 0), ("u", 30)], 30, [("u", 0, 30, 2)]),
        ([("u", 0), ("u", 31)], 30, [("u", 0, 0, 1), ("u", 31, 31, 1)]),
        ([("u", 5), ("u", 5), ("u", 5)], 0, [("u", 5, 5, 3)]),
        ([("u", 1), ("u", 2)], 0, [("u", 1, 1, 1), ("u", 2, 2, 1)]),
        ([("b", 1), ("a", 1)], 5, [("a", 1, 1, 1), ("b", 1, 1, 1)]),
        ([("x", 50), ("x", 10), ("x", 20), ("x", 90)], 15, [("x", 10, 20, 2), ("x", 50, 50, 1), ("x", 90, 90, 1)]),
        ([("a", 0), ("b", 3), ("a", 4), ("b", 100)], 5, [("a", 0, 4, 2), ("b", 3, 3, 1), ("b", 100, 100, 1)]),
        ([("a", -10), ("a", -5)], 5, [("a", -10, -5, 2)]),
    ],
)
def test_examples(events, gap, expected):
    assert _norm(sessionize(events, gap)) == expected


def test_negative_gap():
    with pytest.raises(ValueError):
        sessionize([("a", 1)], -1)


def _oracle(events, gap):
    # Sort all events globally, then sweep keeping each user's open session.
    open_, done = {}, []
    for user, t in sorted(events, key=lambda e: (e[1], e[0])):
        s = open_.get(user)
        if s and t - s[2] <= gap:
            s[2], s[3] = t, s[3] + 1
        else:
            if s:
                done.append(tuple(s))
            open_[user] = [user, t, t, 1]
    done += [tuple(s) for s in open_.values()]
    return sorted(done, key=lambda s: (s[1], s[0]))


def test_random_against_oracle():
    rng = random.Random(92)
    for _ in range(200):
        events = [(rng.choice("abcd"), rng.randint(0, 120)) for _ in range(rng.randint(0, 25))]
        gap = rng.randint(0, 20)
        assert _norm(sessionize(events, gap)) == _oracle(events, gap), (events, gap)
