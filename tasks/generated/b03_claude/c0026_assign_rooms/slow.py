# Correct but naive: for every meeting, re-check all meetings placed so far (O(n^2)).
def assign_rooms(meetings: list[tuple[int, int]]) -> list[int]:
    for start, end in meetings:
        if not start < end:
            raise ValueError("each meeting needs start < end")
    order = sorted(range(len(meetings)), key=lambda i: (meetings[i][0], meetings[i][1], i))
    rooms = [0] * len(meetings)
    placed = []
    opened = 0
    for i in order:
        start, end = meetings[i]
        busy = {rooms[j] for j in placed if meetings[j][1] > start}
        room = next((r for r in range(opened) if r not in busy), None)
        if room is None:
            room = opened
            opened += 1
        rooms[i] = room
        placed.append(i)
    return rooms
