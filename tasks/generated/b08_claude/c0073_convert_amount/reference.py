import re
from collections import deque
from fractions import Fraction

_AMOUNT = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")
_RATE = re.compile(r"[0-9]+(?:\.[0-9]+)?")


def _round_half_even_2(x: Fraction) -> int:
    """x rounded to hundredths, half to even, as an integer number of hundredths."""
    scaled = x * 100
    floor = scaled.numerator // scaled.denominator
    rest = scaled - floor
    if rest > Fraction(1, 2) or (rest == Fraction(1, 2) and floor % 2):
        floor += 1
    return floor


def convert_amount(amount: str, src: str, dst: str, rates: list[tuple[str, str, str]]) -> str:
    if not _AMOUNT.fullmatch(amount):
        raise ValueError(f"bad amount: {amount!r}")
    graph: dict[str, dict[str, Fraction]] = {}
    for a, b, r in rates:
        if not _RATE.fullmatch(r) or Fraction(r) == 0 or a == b or b in graph.get(a, {}):
            raise ValueError(f"bad or duplicate rate {a}->{b}")
        graph.setdefault(a, {})[b] = Fraction(r)
        graph.setdefault(b, {})[a] = 1 / Fraction(r)  # rates work backwards too

    value = Fraction(amount)
    if src != dst:
        # BFS with neighbours in sorted order: the first time a node is reached is via the
        # lexicographically smallest shortest path.
        parent = {src: None}
        queue = deque([src])
        while queue and dst not in parent:
            node = queue.popleft()
            for nxt in sorted(graph.get(node, {})):
                if nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)
        if dst not in parent:
            raise ValueError(f"no path from {src} to {dst}")
        path = [dst]
        while parent[path[-1]] is not None:
            path.append(parent[path[-1]])
        path.reverse()
        for x, y in zip(path, path[1:]):
            value *= graph[x][y]

    cents = _round_half_even_2(value)
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"
