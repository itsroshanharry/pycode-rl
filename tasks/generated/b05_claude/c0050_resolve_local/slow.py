# Naive but correct: test every offset period for every query, O(queries x transitions).
def resolve_local(queries, base_offset, transitions):
    periods = []  # (start or None, end or None, offset)
    prev_start, prev_off = None, base_offset
    for at, off in transitions:
        periods.append((prev_start, at, prev_off))
        prev_start, prev_off = at, off
    periods.append((prev_start, None, prev_off))
    out = []
    for local in queries:
        found = []
        for start, end, off in periods:
            u = local - off
            if (start is None or start <= u) and (end is None or u < end):
                found.append(u)
        out.append(sorted(found))
    return out
