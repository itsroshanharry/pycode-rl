```python
def league_table(results: list[str]) -> list[str]:
    """Rank the teams of a league from match results, best first.

    Each result is "<home> <home goals>-<away goals> <away>", for example
    "Real Madrid 2-1 Bayern Munich". A team name is one or more words of ASCII
    letters separated by single spaces; goals are non-negative integers of
    ASCII digits; there is exactly one space on each side of the score.
    A team cannot play itself. Teams are exactly those that appear in a result.

    A win is worth 3 points, a draw 1, a loss 0. Rank by:
      1. points, 2. goal difference (scored - conceded), 3. goals scored
      (all three higher is better, over all matches).
    Teams still tied on all three form a group. Order each group by a
    head-to-head table built ONLY from the matches between members of that
    group: head-to-head points, then head-to-head goal difference, then
    head-to-head goals scored. This is done once per group (do not re-apply it
    to teams that are still tied). Any remaining ties: team name ascending.

    Raise ValueError for a malformed result or a team playing itself.

    >>> league_table(["A 2-1 C", "B 1-0 A", "D 2-1 B"])
    ['D', 'B', 'A', 'C']
    """
```
