_UNITS = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]


def format_duration(seconds: int, max_units: int = 2) -> str:
    if seconds < 0 or max_units < 1:
        raise ValueError("seconds must be >= 0 and max_units >= 1")
    if seconds == 0:
        return "0s"
    value = seconds
    while True:
        first = next(i for i, (_, size) in enumerate(_UNITS) if size <= value)
        window = _UNITS[first : first + max_units]
        step = window[-1][1]
        rounded = (value + step // 2) // step * step  # half up to the smallest unit
        if rounded >= value and first > 0 and rounded >= _UNITS[first - 1][1]:
            value = rounded  # carried into the next larger unit: start again
            continue
        break
    parts = []
    rest = rounded
    for name, size in window:
        count, rest = divmod(rest, size)
        if count:
            parts.append(f"{count}{name}")
    return " ".join(parts)
