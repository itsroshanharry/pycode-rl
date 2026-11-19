def point_in_polygon(point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
    if len(polygon) < 3:
        raise ValueError("a polygon needs at least 3 vertices")
    px, py = point
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        # On the edge: collinear (zero cross product) and within the bounding box.
        cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
        if cross == 0 and min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2):
            return True
        # Rightward ray; the half-open test (one endpoint strictly above) counts each vertex once.
        if (y1 > py) != (y2 > py):
            lhs = (px - x1) * (y2 - y1)
            rhs = (py - y1) * (x2 - x1)
            if y2 > y1:
                crosses = lhs < rhs
            else:
                crosses = lhs > rhs
            if crosses:
                inside = not inside
    return inside
