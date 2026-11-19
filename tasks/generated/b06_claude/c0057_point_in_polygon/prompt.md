```python
def point_in_polygon(point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
    """Is `point` inside `polygon`, by the even-odd rule, with the boundary counting as inside?

    All coordinates are integers (possibly huge), so the answer must be exact:
    no floating point. `polygon` lists its vertices in order; the last vertex
    connects back to the first. It may be concave or self-intersecting, and
    it may repeat vertices or have collinear vertices.

    Return True if the point lies on any edge (including a vertex), otherwise
    True exactly when a ray from the point crosses the polygon's boundary an
    odd number of times (the even-odd rule; a ray that passes exactly through
    a vertex must be counted consistently, so it does not change the answer).
    Raise ValueError if the polygon has fewer than 3 vertices.

    >>> point_in_polygon((2, 2), [(0, 0), (4, 0), (4, 4), (0, 4)])
    True
    >>> point_in_polygon((4, 3), [(0, 0), (6, 0), (6, 2), (2, 2), (2, 4), (6, 4), (6, 6), (0, 6)])
    False
    """
```
