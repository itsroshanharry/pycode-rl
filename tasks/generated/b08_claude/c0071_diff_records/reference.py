def _same(a, b) -> bool:
    # Python's == says 1 == 1.0 == True; the spec wants type-strict equality at every depth.
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def diff_records(old: dict, new: dict) -> dict[str, list[str]]:
    return {
        "added": sorted(k for k in new if k not in old),
        "removed": sorted(k for k in old if k not in new),
        "changed": sorted(k for k in old if k in new and not _same(old[k], new[k])),
    }
