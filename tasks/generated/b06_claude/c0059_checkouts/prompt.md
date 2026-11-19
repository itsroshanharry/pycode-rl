```python
def checkouts(score: int) -> tuple[int, list[str] | None]:
    """Count the darts checkouts for `score` and pick the preferred one.

    Darts (62 in total), with their values:
      singles "S1".."S20" (1..20) and "SB" (outer bull, 25);
      doubles "D1".."D20" (2..40) and "DB" (bullseye, 50);
      trebles "T1".."T20" (3..60).
    A checkout is 1, 2 or 3 darts whose values add up to `score`, where the
    LAST dart is a double ("D1".."D20" or "DB"). Every dart scores (no misses).
    The order of the darts before the last one does not matter: two checkouts
    are the same if they have the same last dart and the same multiset of
    earlier darts. Darts with equal value are still different darts
    (S6, D3 and T2 are three different darts).

    Return (number of distinct checkouts, preferred checkout), or (0, None)
    if there is none. The preferred checkout uses the fewest darts; among
    those, compare the earlier darts sorted from strongest to weakest and take
    the strongest list (lexicographically), where a dart is stronger if it
    has a higher value, and for equal values a treble beats a double, which
    beats a single. Return it as a list of names: the earlier darts strongest
    first, then the final double.

    >>> checkouts(170)
    (1, ['T20', 'T20', 'DB'])
    >>> checkouts(11)
    (36, ['T3', 'D1'])
    """
```
