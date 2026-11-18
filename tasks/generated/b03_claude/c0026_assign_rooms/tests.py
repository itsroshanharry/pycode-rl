import random

import pytest
from solution import assign_rooms


@pytest.mark.parametrize(
    "meetings, expected",
    [
        ([(0, 30), (5, 10), (15, 20), (10, 15)], [0, 1, 1, 1]),
        ([(1, 4), (1, 3), (3, 5)], [1, 0, 0]),
        ([], []),
        ([(5, 6)], [0]),
        ([(0, 10), (0, 10), (0, 10)], [0, 1, 2]),
        ([(0, 5), (5, 10), (10, 15)], [0, 0, 0]),
        ([(0, 5), (1, 6), (5, 7), (6, 8)], [0, 1, 0, 1]),
        ([(0, 10), (1, 3), (2, 4), (3, 5), (4, 6)], [0, 1, 2, 1, 2]),
        ([(10, 20), (0, 5), (5, 15)], [1, 0, 0]),
        ([(0, 4), (0, 2), (2, 3), (3, 5), (4, 6)], [1, 0, 0, 0, 1]),
        ([(0, 100), (1, 2), (2, 3), (50, 60), (1, 5)], [0, 1, 1, 1, 2]),
    ],
)
def test_examples(meetings, expected):
    assert list(assign_rooms(meetings)) == expected


@pytest.mark.parametrize("meetings", [[(3, 3)], [(0, 5), (7, 6)]])
def test_invalid(meetings):
    with pytest.raises(ValueError):
        assign_rooms(meetings)


def _brute(meetings):
    order = sorted(range(len(meetings)), key=lambda i: (meetings[i][0], meetings[i][1], i))
    rooms, room_end = [0] * len(meetings), []
    for i in order:
        s, e = meetings[i]
        r = next((k for k, end in enumerate(room_end) if end <= s), len(room_end))
        if r == len(room_end):
            room_end.append(e)
        else:
            room_end[r] = e
        rooms[i] = r
    return rooms


def test_random_against_brute_force():
    rng = random.Random(51)
    for _ in range(150):
        meetings = []
        for _ in range(rng.randint(0, 25)):
            s = rng.randint(0, 40)
            meetings.append((s, s + rng.randint(1, 12)))
        assert list(assign_rooms(meetings)) == _brute(meetings), meetings


def _check_large(meetings, rooms):
    # Valid (no overlaps within a room) and optimal (rooms used == maximum overlap).
    by_room = {}
    for (s, e), r in zip(meetings, rooms):
        by_room.setdefault(r, []).append((s, e))
    for intervals in by_room.values():
        intervals.sort()
        assert all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:]))
    events = sorted([(s, 1) for s, _ in meetings] + [(e, -1) for _, e in meetings])
    depth = peak = 0
    for _, d in events:
        depth += d
        peak = max(peak, depth)
    assert sorted(by_room) == list(range(peak))


def test_large_all_overlapping():
    meetings = [(i, 10**9 - i) for i in range(30_000)]
    rooms = list(assign_rooms(meetings))
    assert rooms == list(range(30_000))


def test_large_random():
    rng = random.Random(7)
    meetings = []
    for _ in range(30_000):
        s = rng.randint(0, 10**6)
        meetings.append((s, s + rng.randint(1, 5_000)))
    _check_large(meetings, list(assign_rooms(meetings)))
