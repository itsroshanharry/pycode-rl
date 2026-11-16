[
    ("FIFO queue instead of a min-heap (not lexicographically smallest)", "                heapq.heappush(ready, v)", "                ready.append(v)"),
    ("cycles not detected (returns a partial order)", "    return order if len(order) == n else []", "    return order"),
    ("duplicate edges deduplicated in adjacency but not in indegree", "        adjacency[u].append(v)\n", "        if v not in adjacency[u]:\n            adjacency[u].append(v)\n"),
]
