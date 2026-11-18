def ffill_limited(values: list, limit: int) -> list:
    if limit < 0:
        raise ValueError("limit must be >= 0")
    out = []
    last, have, run = None, False, 0
    for v in values:
        if v is None:
            run += 1
            out.append(last if have and run <= limit else None)
        else:
            out.append(v)
            last, have = v, True
            run = 0
    return out
