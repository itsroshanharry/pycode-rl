_DARTS: dict[str, tuple[int, int]] = {}  # name -> (value, kind rank: treble 2 > double 1 > single 0)
for _i in range(1, 21):
    _DARTS[f"S{_i}"] = (_i, 0)
    _DARTS[f"D{_i}"] = (2 * _i, 1)
    _DARTS[f"T{_i}"] = (3 * _i, 2)
_DARTS["SB"] = (25, 0)
_DARTS["DB"] = (50, 1)
_NAMES = list(_DARTS)
_DOUBLES = [n for n in _NAMES if n.startswith("D")]


def _strength(name: str) -> tuple[int, int]:
    return _DARTS[name]


def checkouts(score: int) -> tuple[int, list[str] | None]:
    found: set[tuple[tuple[str, ...], str]] = set()
    for final in _DOUBLES:
        rest = score - _DARTS[final][0]
        if rest == 0:
            found.add(((), final))
        for i, a in enumerate(_NAMES):
            va = _DARTS[a][0]
            if va == rest:
                found.add(((a,), final))
            # earlier darts are unordered: each pair once (b from position i on), stored sorted
            for b in _NAMES[i:]:
                if va + _DARTS[b][0] == rest:
                    found.add((tuple(sorted((a, b))), final))
    if not found:
        return 0, None

    def key(c):
        earlier = sorted(c[0], key=_strength, reverse=True)
        return (len(earlier), [(-_DARTS[n][0], -_DARTS[n][1]) for n in earlier])

    best = min(found, key=key)
    return len(found), sorted(best[0], key=_strength, reverse=True) + [best[1]]
