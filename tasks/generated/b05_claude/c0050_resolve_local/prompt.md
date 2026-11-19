```python
def resolve_local(queries: list[int], base_offset: int, transitions: list[tuple[int, int]]) -> list[list[int]]:
    """Map local wall-clock times back to UTC instants, given UTC-offset changes.

    All times are integer minutes on one shared count. For a UTC instant u,
    the local time is u + offset(u), where:
    - offset(u) = base_offset for every u before the first transition;
    - a transition (at, new_offset) sets offset(u) = new_offset for all
      u >= at, until the next transition.
    `transitions` is sorted by strictly increasing `at`.

    For each local time L in `queries`, return the sorted list of ALL UTC
    instants u with u + offset(u) == L. A local time skipped when clocks jump
    forward gives [], a local time repeated when clocks go back gives two
    instants, and any other local time gives one.

    Guarantees (no need to check): every offset is between -1440 and 1440,
    consecutive transitions are more than 2880 minutes apart, and there can be
    up to 40 000 queries and 20 000 transitions in one call.

    >>> resolve_local([1059, 1060, 1120, 5060, 5120], 60, [(1000, 120), (5000, 60)])
    [[999], [], [1000], [4940, 5000], [5060]]
    """
```
