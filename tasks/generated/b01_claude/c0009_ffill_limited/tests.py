import random

import pytest
from solution import ffill_limited


@pytest.mark.parametrize(
    "values, limit, expected",
    [
        ([1, None, None, None, 5, None], 2, [1, 1, 1, None, 5, 5]),
        ([None, 0, None], 1, [None, 0, 0]),
        ([], 3, []),
        ([None, None], 5, [None, None]),
        ([1, None, None], 0, [1, None, None]),
        ([1, None, 2, None, None, None], 1, [1, 1, 2, 2, None, None]),
        (["", None, None], 5, ["", "", ""]),
        ([False, None], 1, [False, False]),
        ([0.0, None, 3, None, None], 10, [0.0, 0.0, 3, 3, 3]),
        ([None, 7, None, None, 8], 2, [None, 7, 7, 7, 8]),
        ([5], 1, [5]),
        ([1, None, None, None, None, 2, None, None], 3, [1, 1, 1, 1, None, 2, 2, 2]),
        (["a", None, "b", None], 1, ["a", "a", "b", "b"]),
    ],
)
def test_examples(values, limit, expected):
    result = list(ffill_limited(values, limit))
    assert result == expected
    assert [type(x) for x in result] == [type(x) for x in expected]


def test_negative_limit():
    with pytest.raises(ValueError):
        ffill_limited([1, None], -1)


def _oracle(values, limit):
    out = []
    for i, v in enumerate(values):
        if v is not None:
            out.append(v)
            continue
        j = i - 1
        while j >= 0 and values[j] is None:
            j -= 1
        out.append(values[j] if j >= 0 and i - j <= limit else None)
    return out


def test_random_against_oracle():
    rng = random.Random(93)
    for _ in range(200):
        values = [rng.choice([None, None, 0, 1, 2.5, "", "x", False]) for _ in range(rng.randint(0, 20))]
        limit = rng.randint(0, 4)
        assert list(ffill_limited(values, limit)) == _oracle(values, limit), (values, limit)
