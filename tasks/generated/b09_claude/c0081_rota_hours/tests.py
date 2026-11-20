import random

import pytest
from solution import rota_hours

# Expected values below were computed with an independent day-by-day brute force.
@pytest.mark.parametrize(
    "args, expected",
    [
        (([10, 0, 13], {"ana": 0, "bo": 1}, 0, 5, [2, 2, 99]), {"ana": "70.0", "bo": "54.0"}),
        (([8], {"w": 0}, 1, 1, []), {"w": "8.0"}),
        (([9], {"w": 0}, 1, 1, []), {"w": "9.5"}),
        (([12], {"w": 0}, 1, 1, []), {"w": "14.0"}),
        (([13], {"w": 0}, 1, 1, []), {"w": "16.0"}),
        (([24], {"w": 0}, 1, 1, [1]), {"w": "76.0"}),
        (([0], {"w": 0}, -5, 5, [0]), {"w": "0.0"}),
        (([1, 2, 3], {"a": 0, "b": 1, "c": -1, "d": 4}, -7, 3, [-7, -7, 3, 4, -8]), {"a": "26.0", "b": "28.0", "c": "24.0", "d": "28.0"}),
        (([5, 10], {"x": 0}, 0, 0, [0]), {"x": "10.0"}),
        (([11, 0, 0, 9], {"z": -3, "y": 10 ** 12}, -10, 10, [0, 5, -10, 10]), {"z": "132.0", "y": "122.5"}),
        (([7], {}, 0, 10, []), {}),
        (([10, 0, 13], {"ana": 0}, 10, 10, [10]), {"ana": "0.0"}),
    ],
)
def test_examples(args, expected):
    got = rota_hours(*args)
    assert got == expected
    assert list(got) == list(expected)


@pytest.mark.parametrize(
    "args",
    [([8], {"w": 0}, 2, 1, []), ([], {"w": 0}, 0, 1, []), ([8, 25], {"w": 0}, 0, 1, []), ([-1], {"w": 0}, 0, 1, [])],
)
def test_invalid(args):
    with pytest.raises(ValueError):
        rota_hours(*args)


def _paid(h):
    return 2 * min(h, 8) + 3 * max(0, min(h, 12) - 8) + 4 * max(0, h - 12)


def _brute(pattern, offsets, a, b, holidays):
    hol = set(holidays)
    out = {}
    for w, k in offsets.items():
        t = sum(_paid(pattern[(d - k) % len(pattern)]) * (2 if d in hol else 1) for d in range(a, b + 1))
        out[w] = f"{t // 2}.{5 if t % 2 else 0}"
    return out


def _count_formula(pattern, offsets, a, b, holidays):
    # independent closed form: number of days d in [a, b] with (d - k) % L == i
    L = len(pattern)
    hol = {h for h in holidays if a <= h <= b}
    out = {}
    for w, k in offsets.items():
        t = 0
        for i, h in enumerate(pattern):
            n = (b - k - i) // L - (a - 1 - k - i) // L
            t += n * _paid(h)
        t += sum(_paid(pattern[(d - k) % L]) for d in hol)
        out[w] = f"{t // 2}.{5 if t % 2 else 0}"
    return out


def test_random_against_brute_force():
    rng = random.Random(53)
    for _ in range(300):
        pattern = [rng.choice([0, 0, 4, 8, 9, 10, 12, 13, 24]) for _ in range(rng.randint(1, 6))]
        offsets = {f"w{i}": rng.randint(-20, 20) for i in range(rng.randint(0, 4))}
        a = rng.randint(-30, 30)
        b = a + rng.randint(0, 40)
        holidays = [rng.randint(a - 5, b + 5) for _ in range(rng.randint(0, 8))]
        assert rota_hours(pattern, offsets, a, b, holidays) == _brute(pattern, offsets, a, b, holidays)


def test_huge_range():
    # 2 * 10**12 + 1 days, 50 workers, 5000 holidays: walking day by day is impossible.
    rng = random.Random(1053)
    pattern = [rng.choice([0, 8, 9, 10, 12, 13, 24]) for _ in range(997)]
    offsets = {f"w{i}": rng.randint(-10 ** 13, 10 ** 13) for i in range(50)}
    a, b = -10 ** 12, 10 ** 12
    holidays = [rng.randint(a, b) for _ in range(5000)] + [a, b, a - 1, b + 1]
    assert rota_hours(pattern, offsets, a, b, holidays) == _count_formula(pattern, offsets, a, b, holidays)
