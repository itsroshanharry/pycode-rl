```python
def round_robin(teams: list[str]) -> list[list[tuple[str, str]]]:
    """Round-robin tournament schedule built with the circle method.

    `teams` has at least 2 unique names, none of them "BYE". If the number of teams
    is odd, append the placeholder "BYE" so the count n is even. There are n - 1
    rounds. For round r (r = 0, 1, ..., n - 2), build an arrangement of length n:
    position 0 is always the first team, and positions 1..n-1 hold the other n - 1
    entries (in their original order) rotated right by r steps, so that in round 1
    the last entry moves to position 1. Then pair position i with position n-1-i,
    for i = 0, 1, ..., n/2 - 1, giving matches (arrangement[i], arrangement[n-1-i])
    in that order of i. Leave out any match involving "BYE".
    Return the list of rounds, each a list of (team, team) tuples.
    Raise ValueError for fewer than 2 teams, duplicate names, or a team named "BYE".

    >>> round_robin(["A", "B", "C", "D"])
    [[('A', 'D'), ('B', 'C')], [('A', 'C'), ('D', 'B')], [('A', 'B'), ('C', 'D')]]
    >>> round_robin(["A", "B", "C"])
    [[('B', 'C')], [('A', 'C')], [('A', 'B')]]
    """
```
