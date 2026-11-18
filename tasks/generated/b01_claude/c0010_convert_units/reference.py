import re
from collections import deque
from fractions import Fraction

_NUM = re.compile(r"(-?)([0-9]+(?:\.[0-9]+)?|[0-9]+/[0-9]+)")


def _number(s: str, allow_negative: bool) -> Fraction:
    m = _NUM.fullmatch(s) if isinstance(s, str) else None
    if not m or (m.group(1) and not allow_negative):
        raise ValueError(f"malformed number: {s!r}")
    body = m.group(2)
    if "/" in body:
        p, q = body.split("/")
        if int(q) == 0:
            raise ValueError(f"zero denominator: {s!r}")
        value = Fraction(int(p), int(q))
    else:
        value = Fraction(body)
    return -value if m.group(1) else value


def convert_units(amount: str, from_unit: str, to_unit: str, factors: list[tuple[str, str, str]]) -> str:
    value = _number(amount, allow_negative=True)
    graph: dict[str, list[tuple[str, Fraction]]] = {}
    for a, b, f in factors:
        r = _number(f, allow_negative=False)
        if r == 0:
            raise ValueError("factors must be positive")
        graph.setdefault(a, []).append((b, r))
        graph.setdefault(b, []).append((a, 1 / r))
    ratio = {from_unit: Fraction(1)}  # how many of each unit one from_unit is
    queue = deque([from_unit])
    while queue:
        u = queue.popleft()
        for v, r in graph.get(u, []):
            if v not in ratio:
                ratio[v] = ratio[u] * r
                queue.append(v)
    if to_unit not in ratio:
        raise ValueError(f"no conversion from {from_unit!r} to {to_unit!r}")
    result = value * ratio[to_unit]
    return str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"
