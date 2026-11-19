from bisect import bisect_right

_MAX_OFFSET = 1440


def resolve_local(queries: list[int], base_offset: int, transitions: list[tuple[int, int]]) -> list[list[int]]:
    starts = [at for at, _ in transitions]
    offsets = [base_offset] + [off for _, off in transitions]  # offsets[k] holds for starts[k-1] <= u < starts[k]
    out = []
    for local in queries:
        # Any solution u = local - offset lies in [local - 1440, local + 1440], so only the
        # periods overlapping that window can contribute (at most 2, given the spacing).
        lo = bisect_right(starts, local - _MAX_OFFSET)
        hi = bisect_right(starts, local + _MAX_OFFSET)
        found = []
        for k in range(lo, hi + 1):
            u = local - offsets[k]
            if (k == 0 or starts[k - 1] <= u) and (k == len(starts) or u < starts[k]):
                found.append(u)
        out.append(found)  # periods are in time order, so found is already sorted
    return out
