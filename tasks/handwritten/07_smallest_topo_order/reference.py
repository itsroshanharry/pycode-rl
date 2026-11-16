import heapq


def smallest_topo_order(n: int, edges: list[tuple[int, int]]) -> list[int]:
    indegree = [0] * n
    adjacency: list[list[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        indegree[v] += 1
    ready = [v for v in range(n) if indegree[v] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        u = heapq.heappop(ready)
        order.append(u)
        for v in adjacency[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(ready, v)
    return order if len(order) == n else []
