```python
def assign_rooms(meetings: list[tuple[int, int]]) -> list[int]:
    """Assign every meeting to a numbered room.

    Each meeting is (start, end) with integers start < end, occupying the half-open
    interval [start, end). Process meetings in order of start time, ties by end
    time, then by position in the input list. Each meeting takes the free room with
    the lowest number, where a room is free if every meeting already placed in it
    has ended at or before this meeting's start. If no room is free, open a new
    room; rooms are numbered 0, 1, 2, ... in the order they are opened.
    Return the room number of each meeting, in input order.
    Up to 30_000 meetings with times in 0..10**9; your solution must handle that
    size in well under a second. Raise ValueError if some meeting has start >= end.

    >>> assign_rooms([(0, 30), (5, 10), (15, 20), (10, 15)])
    [0, 1, 1, 1]
    >>> assign_rooms([(1, 4), (1, 3), (3, 5)])
    [1, 0, 0]
    """
```
