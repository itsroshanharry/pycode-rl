import random
from fractions import Fraction

import pytest
from solution import point_in_polygon

SQ = [(0, 0), (4, 0), (4, 4), (0, 4)]
C = [(0, 0), (6, 0), (6, 2), (2, 2), (2, 4), (6, 4), (6, 6), (0, 6)]
TRI = [(0, 0), (4, 2), (0, 4)]
BOW = [(0, 0), (4, 4), (4, 0), (0, 4)]


@pytest.mark.parametrize(
    "point, polygon, expected",
    [
        ((2, 2), SQ, True), ((5, 2), SQ, False), ((4, 2), SQ, True), ((0, 0), SQ, True), ((2, 4), SQ, True),
        ((2, 5), SQ, False), ((-1, 0), SQ, False), ((5, 0), SQ, False), ((-1, 4), SQ, False), ((0, 2), SQ, True),
        ((4, 3), C, False), ((1, 3), C, True), ((4, 1), C, True), ((4, 5), C, True), ((1, 2), C, True),
        ((-1, 2), C, False), ((-1, 4), C, False), ((3, 2), C, True), ((7, 2), C, False), ((2, 3), C, True),
        ((3, 3), C, False), ((-1, 6), C, False), ((6, 6), C, True),
        ((-1, 2), TRI, False), ((1, 2), TRI, True), ((4, 2), TRI, True), ((5, 2), TRI, False), ((2, 1), TRI, True),
        ((3, 1), TRI, False), ((2, 3), TRI, True),
        ((2, 2), BOW, True), ((1, 2), BOW, True), ((2, 1), BOW, False), ((3, 2), BOW, True), ((2, 3), BOW, False),
        ((1, 1), [(0, 0), (2, 0), (2, 0), (2, 2), (0, 2)], True),
        ((1, 0), [(0, 0), (2, 0), (2, 0), (2, 2), (0, 2)], True),
        ((3, 0), [(0, 0), (1, 0), (2, 0), (2, 2), (0, 2)], False),
        ((10 ** 12 - 1, 1), [(0, 0), (10 ** 12, 0), (10 ** 12, 10 ** 12)], True),
        ((10 ** 12 - 1, 2), [(0, 0), (10 ** 12, 0), (10 ** 12, 10 ** 12)], True),
        ((1, 2), [(0, 0), (10 ** 12, 0), (10 ** 12, 10 ** 12)], False),
        ((10 ** 12, 10 ** 12 + 1), [(0, 0), (10 ** 12, 0), (10 ** 12, 10 ** 12)], False),
        ((1, 1), [(0, 0), (3, 1), (0, 3)], True),
        ((3, 1), [(0, 0), (3, 1), (0, 3)], True),
        ((2, 2), [(0, 0), (3, 1), (0, 3)], False),
        ((0, 1), [(0, 0), (2, 0), (0, 2), (2, 2)], False),
        ((1, 0), [(0, 0), (2, 0), (0, 2), (2, 2)], True),
        ((1, 1), [(0, 0), (2, 0), (0, 2), (2, 2)], True),
    ],
)
def test_examples(point, polygon, expected):
    assert point_in_polygon(point, polygon) is expected


@pytest.mark.parametrize("polygon", [[], [(0, 0)], [(0, 0), (1, 1)]])
def test_invalid(polygon):
    with pytest.raises(ValueError):
        point_in_polygon((0, 0), polygon)


def _on_segment(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    return (bx - ax) * (py - ay) == (by - ay) * (px - ax) and min(ax, bx) <= px <= max(ax, bx) and min(ay, by) <= py <= max(ay, by)


def _oracle(p, poly):
    n = len(poly)
    if any(_on_segment(p, poly[i], poly[(i + 1) % n]) for i in range(n)):
        return True
    # Ray in direction (1000003, 1): with |coords| <= 30 it can never pass through a vertex.
    dx, dy = 1000003, 1
    count = 0
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if den == 0:
            continue
        wx, wy = ax - p[0], ay - p[1]
        t = Fraction(wx * ey - wy * ex, den)
        s = Fraction(wx * dy - wy * dx, den)
        if t > 0 and 0 <= s <= 1:
            count += 1
    return count % 2 == 1


def test_random_against_oracle():
    rng = random.Random(74)
    for _ in range(600):
        poly = [(rng.randint(-10, 10), rng.randint(-10, 10)) for _ in range(rng.randint(3, 8))]
        p = (rng.randint(-12, 12), rng.randint(-12, 12))
        if rng.random() < 0.3:
            p = (rng.choice(poly)[0], rng.choice(poly)[1])  # share a coordinate with vertices
        assert point_in_polygon(p, poly) is _oracle(p, poly), (p, poly)
