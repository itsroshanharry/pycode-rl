def _sort_key(group: tuple) -> tuple:
    # None first in each column; comparing None with an int/str directly would raise.
    return tuple((0,) if x is None else (1, x) for x in group)


def group_aggregate(rows: list[dict], keys: list[str], value: str) -> list[tuple]:
    stats: dict[tuple, list] = {}  # group -> [count, sum, min, max]
    for row in rows:
        group = tuple(row.get(k) for k in keys)
        s = stats.setdefault(group, [0, 0, None, None])
        s[0] += 1  # every row counts
        v = row.get(value)
        if v is not None:
            s[1] += v
            s[2] = v if s[2] is None else min(s[2], v)
            s[3] = v if s[3] is None else max(s[3], v)
    return [(*g, *stats[g]) for g in sorted(stats, key=_sort_key)]
