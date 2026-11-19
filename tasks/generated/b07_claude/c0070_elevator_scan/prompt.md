```python
def elevator_scan(start: int, direction: str, requests: list[int], top: int) -> tuple[list[int], int]:
    """Serve elevator requests in SCAN order; return (service order, floors travelled).

    Floors are 0..top (top >= 0). The car starts at `start` moving in
    `direction` ("up" or "down"). `requests` are floors; repeated floors are
    one request.
    - A request at the start floor is served first, without moving.
    - The car then moves in `direction`, serving every requested floor it
      reaches, in order.
    - SCAN rule (not LOOK): if any requests remain on the other side of the
      start floor, the car first continues all the way to the END floor
      (top when moving up, 0 when moving down), even if there are no requests
      between the start and that end, then reverses and serves the remaining
      floors in order, stopping at the last one.
    - If no requests remain on the other side, the car stops at the last
      floor it served (it does not go on to the end).
    Raise ValueError for a bad direction, top < 0, or a floor (start or
    request) outside 0..top.

    >>> elevator_scan(5, "up", [7, 2, 9], 10)
    ([7, 9, 2], 13)
    >>> elevator_scan(5, "up", [2], 10)
    ([2], 13)
    """
```
