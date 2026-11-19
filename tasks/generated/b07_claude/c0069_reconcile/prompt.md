```python
def reconcile(a: list[tuple[int, int, int]], b: list[tuple[int, int, int]], tol: int) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    """Reconcile two ledgers by amount and date tolerance.

    Each entry is (id, day, amount): integers (ids are labels; days and
    amounts may be negative). Process the entries of `a` in order. Each one is
    matched with an UNMATCHED entry of `b` that has the same amount and a day
    within `tol` days (|day_a - day_b| <= tol). If there are several, take the
    one with the smallest |day difference|; if still tied, the one with the
    EARLIER day; if still tied, the one that comes first in `b`. Once matched,
    a `b` entry cannot be matched again. If there is no candidate, the `a`
    entry stays unmatched (later `a` entries do not reconsider earlier ones).

    Return (matches, unmatched_a, unmatched_b): matches are (a_id, b_id) in
    the order of `a`; unmatched_a are ids in the order of `a`; unmatched_b are
    ids in the order of `b`. Raise ValueError if tol < 0.

    Each ledger can have up to 20 000 entries, possibly all with the same
    amount, so comparing every `a` entry with every `b` entry is too slow.

    >>> reconcile([(1, 10, 500), (2, 10, 500)], [(101, 9, 500), (102, 10, 500), (103, 30, 500)], 1)
    ([(1, 102), (2, 101)], [], [103])
    """
```
