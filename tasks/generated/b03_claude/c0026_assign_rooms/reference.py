import heapq


def assign_rooms(meetings: list[tuple[int, int]]) -> list[int]:
    for start, end in meetings:
        if not start < end:
            raise ValueError("each meeting needs start < end")
    order = sorted(range(len(meetings)), key=lambda i: (meetings[i][0], meetings[i][1], i))
    busy: list[tuple[int, int]] = []  # (end, room) of rooms in use
    free: list[int] = []  # numbers of rooms that are free again
    rooms = [0] * len(meetings)
    opened = 0
    for i in order:
        start, end = meetings[i]
        while busy and busy[0][0] <= start:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            room = heapq.heappop(free)
        else:
            room = opened
            opened += 1
        rooms[i] = room
        heapq.heappush(busy, (end, room))
    return rooms
