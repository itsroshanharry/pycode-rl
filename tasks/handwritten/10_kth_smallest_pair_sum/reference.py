def kth_smallest_pair_sum(a: list[int], b: list[int], k: int) -> int:
    n, m = len(a), len(b)
    if not 1 <= k <= n * m:
        raise ValueError("k out of range")
    a, b = sorted(a), sorted(b)

    def count_at_most(x: int) -> int:
        count, j = 0, m - 1
        for v in a:  # a ascending, so the usable prefix of b only shrinks
            while j >= 0 and v + b[j] > x:
                j -= 1
            count += j + 1
        return count

    lo, hi = a[0] + b[0], a[-1] + b[-1]
    while lo < hi:
        mid = (lo + hi) // 2
        if count_at_most(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
