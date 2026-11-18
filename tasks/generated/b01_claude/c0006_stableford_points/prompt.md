```python
def stableford_points(strokes: list[int], pars: list[int], stroke_index: list[int], handicap: int) -> int:
    """Total Stableford points for one golf round.

    The three lists describe the same holes in order and have the same length N,
    with 1 <= N <= 18. `stroke_index` is a permutation of 1..N ranking the holes
    (1 = hardest). With handicap H >= 0, every hole receives H // N handicap
    strokes, and each hole whose stroke index is <= H % N receives one more.
    On each hole, net = strokes - handicap strokes received, and the hole scores
    max(0, 2 + par - net) points. A stroke count of 0 means the player picked up
    and that hole scores 0 points. Return the total over all holes.
    Raise ValueError if the lengths differ or N is outside 1..18, if stroke_index is
    not a permutation of 1..N, if any par is outside 3..6, if any stroke count is
    negative, or if the handicap is negative.

    >>> stableford_points([5, 3, 7], [4, 3, 5], [2, 3, 1], 2)
    5
    >>> stableford_points([0, 2, 4], [4, 3, 4], [1, 2, 3], 4)
    7
    """
```
