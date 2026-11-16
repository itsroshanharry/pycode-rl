def compress_ranges(nums: list[int]) -> str:
    vals = sorted(set(nums))
    out = []
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[j + 1] == vals[j] + 1:
            j += 1
        if j - i + 1 >= 3:
            out.append(f"{vals[i]}..{vals[j]}")
        else:
            out.extend(str(v) for v in vals[i : j + 1])
        i = j + 1
    return ",".join(out)
