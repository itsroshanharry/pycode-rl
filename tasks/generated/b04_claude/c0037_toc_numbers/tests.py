import random

import pytest
from solution import toc_numbers


@pytest.mark.parametrize(
    "headings, expected",
    [
        ([(1, "Intro"), (2, "Goals"), (2, "Scope"), (1, "Design"), (3, "Detail"), (2, "API")],
         ["1 Intro", "1.1 Goals", "1.2 Scope", "2 Design", "2.1 Detail", "2.2 API"]),
        ([], []),
        ([(3, "x"), (3, "y")], ["1 x", "2 y"]),
        ([(2, "a"), (1, "b"), (2, "c")], ["1 a", "2 b", "2.1 c"]),
        ([(1, "a"), (2, "b"), (3, "c"), (2, "d"), (3, "e"), (3, "f")], ["1 a", "1.1 b", "1.1.1 c", "1.2 d", "1.2.1 e", "1.2.2 f"]),
        ([(1, "a"), (6, "deep"), (6, "deeper?"), (2, "b")], ["1 a", "1.1 deep", "1.2 deeper?", "1.3 b"]),
        ([(2, "a"), (3, "b"), (1, "c"), (3, "d")], ["1 a", "1.1 b", "2 c", "2.1 d"]),
        ([(1, "same title"), (1, "same title")], ["1 same title", "2 same title"]),
        ([(4, "x"), (2, "y"), (3, "z"), (4, "w")], ["1 x", "2 y", "2.1 z", "2.1.1 w"]),
        ([(1, "")], ["1 "]),
    ],
)
def test_examples(headings, expected):
    assert list(toc_numbers(headings)) == expected


@pytest.mark.parametrize("headings", [[(0, "x")], [(7, "x")], [(1, "a"), (2.0, "b")], [(True, "x")]])
def test_invalid(headings):
    with pytest.raises(ValueError):
        toc_numbers(headings)


def _oracle(headings):
    parents = []
    for i, (lvl, _) in enumerate(headings):
        parents.append(next((j for j in range(i - 1, -1, -1) if headings[j][0] < lvl), None))
    numbers = []
    for i in range(len(headings)):
        pos = sum(1 for j in range(i + 1) if parents[j] == parents[i])
        numbers.append(str(pos) if parents[i] is None else f"{numbers[parents[i]]}.{pos}")
    return [f"{n} {t}" for n, (_, t) in zip(numbers, headings)]


def test_random_against_oracle():
    rng = random.Random(23)
    for _ in range(200):
        headings = [(rng.randint(1, 4), rng.choice(["a", "b", "c"])) for _ in range(rng.randint(0, 15))]
        assert list(toc_numbers(headings)) == _oracle(headings), headings
