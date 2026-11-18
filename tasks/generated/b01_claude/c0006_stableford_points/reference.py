def stableford_points(strokes: list[int], pars: list[int], stroke_index: list[int], handicap: int) -> int:
    n = len(strokes)
    if not 1 <= n <= 18 or len(pars) != n or len(stroke_index) != n:
        raise ValueError("need 1-18 holes and three lists of the same length")
    if sorted(stroke_index) != list(range(1, n + 1)):
        raise ValueError("stroke_index must be a permutation of 1..N")
    if any(p not in (3, 4, 5, 6) for p in pars):
        raise ValueError("par must be between 3 and 6")
    if any(s < 0 for s in strokes):
        raise ValueError("stroke counts cannot be negative")
    if handicap < 0:
        raise ValueError("handicap must be >= 0")
    total = 0
    for s, par, si in zip(strokes, pars, stroke_index):
        if s == 0:  # picked up
            continue
        received = handicap // n + (1 if si <= handicap % n else 0)
        net = s - received
        total += max(0, 2 + par - net)
    return total
