[
    ("a room is not free when its meeting ends exactly at the start", "        while busy and busy[0][0] <= start:", "        while busy and busy[0][0] < start:"),
    ("ties on start not broken by end time", "key=lambda i: (meetings[i][0], meetings[i][1], i))", "key=lambda i: (meetings[i][0], i))"),
    ("most recently freed room reused instead of the lowest number", "            room = heapq.heappop(free)", "            room = max(free)\n            free.remove(room)\n            heapq.heapify(free)"),
]
