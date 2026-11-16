```python
def smallest_topo_order(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """Order the nodes 0..n-1 so that for every edge (u, v), u comes before v.

    Among all valid orders, return the lexicographically smallest one. If no valid
    order exists (the graph has a cycle, including a self-loop), return an empty
    list. Duplicate edges may occur. n >= 0 and every edge endpoint is in 0..n-1.

    >>> smallest_topo_order(4, [(2, 0), (1, 0), (3, 2)])
    [1, 3, 2, 0]
    >>> smallest_topo_order(2, [(0, 1), (1, 0)])
    []
    """
```
