import itertools
import random

import pytest
from solution import league_table


@pytest.mark.parametrize(
    "results, expected",
    [
        (["A 2-1 C", "B 1-0 A", "D 2-1 B"], ["D", "B", "A", "C"]),
        ([], []),
        (["Real Madrid 2-1 Bayern Munich"], ["Real Madrid", "Bayern Munich"]),
        (["Bb 1-1 Aa"], ["Aa", "Bb"]),
        (["A 1-0 B", "B 1-0 C", "C 1-0 A"], ["A", "B", "C"]),
        (["A 1-0 B", "B 2-0 A"], ["B", "A"]),
        # goals scored decides overall, before any head-to-head (Y beat X)
        (["Y 2-0 X", "X 5-2 Z", "W 1-0 Y"], ["X", "Y", "W", "Z"]),
        # three-way tie settled by the mini-table among P, Q, R only (Oak's matches excluded)
        (["P 3-0 Q", "Q 1-0 R", "R 1-0 P", "Oak 5-0 P", "Oak 3-2 Q", "Oak 5-2 R"], ["Oak", "P", "R", "Q"]),
        # two-way tie settled by head-to-head goal difference, against name order
        (["Zed 3-1 Amy", "Amy 1-0 Zed", "Oak 3-0 Zed", "Oak 2-1 Amy"], ["Oak", "Zed", "Amy"]),
        (["Ab 10-0 Cd", "Cd 0-0 Ef"], ["Ab", "Ef", "Cd"]),
        (["lions 1-0 Lions"], ["lions", "Lions"]),
        (["A 0-0 B", "C 0-0 D"], ["A", "B", "C", "D"]),
        (["A 007-0 B"], ["A", "B"]),
    ],
)
def test_examples(results, expected):
    assert list(league_table(results)) == expected


@pytest.mark.parametrize(
    "result",
    [
        "A 1-0", "A 1:0 B", "A -1-0 B", "A 1-0 A", "A1-0 B", " A 1-0 B", "A  1-0 B", "A 1-0 B ",
        "A 1 - 0 B", "A2 1-0 B", "Ä 1-0 B", "A 1-0 B 2-0 C", "A 1--0 B", "A 1-0  B", "1-0", "A B",
        "A 1-０ B",
    ],
)
def test_invalid(result):
    with pytest.raises(ValueError):
        league_table(["Xx 1-0 Yy", result])


def _oracle(matches):
    def stats(ms, teams):
        s = {t: [0, 0, 0] for t in teams}
        for h, hg, ag, a in ms:
            s[h][0] += 3 * (hg > ag) + (hg == ag)
            s[a][0] += 3 * (ag > hg) + (hg == ag)
            s[h][1] += hg - ag
            s[a][1] += ag - hg
            s[h][2] += hg
            s[a][2] += ag
        return s

    teams = {t for h, _, _, a in matches for t in (h, a)}
    s = stats(matches, teams)
    out = []
    ranked = sorted(teams, key=lambda t: [-x for x in s[t]])
    for _, grp in itertools.groupby(ranked, key=lambda t: s[t]):
        grp = list(grp)
        h = stats([m for m in matches if m[0] in grp and m[3] in grp], grp)
        out += sorted(grp, key=lambda t: ([-x for x in h[t]], t))
    return out


def test_random_against_oracle():
    rng = random.Random(70)
    names = ["Ant", "Bee", "Cat", "Dog", "Eel", "Fox"]
    for _ in range(300):
        matches = []
        for _ in range(rng.randint(0, 10)):
            h, a = rng.sample(names[: rng.randint(2, 6)], 2)
            matches.append((h, rng.randint(0, 2), rng.randint(0, 2), a))
        results = [f"{h} {hg}-{ag} {a}" for h, hg, ag, a in matches]
        assert list(league_table(results)) == _oracle(matches), results
