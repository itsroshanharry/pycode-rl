def unpack_bits(value: int, layout: list[tuple[str, int, int]]) -> dict[str, int]:
    if value < 0:
        raise ValueError("value must be non-negative")
    fields = []
    seen: set[str] = set()
    for name, offset, width in layout:
        signed = name.endswith("!")
        key = name[:-1] if signed else name
        if not key or key in seen:
            raise ValueError(f"empty or duplicate key: {name!r}")
        if offset < 0 or width < 1:
            raise ValueError(f"bad offset/width for {name!r}")
        seen.add(key)
        fields.append((offset, width, key, signed))
    fields.sort()

    covered, prev_end = 0, 0
    for offset, width, key, _ in fields:
        if offset < prev_end:
            raise ValueError(f"field {key!r} overlaps the previous field")
        prev_end = offset + width
        covered |= ((1 << width) - 1) << offset
    if value & ~covered:
        raise ValueError("value has bits outside every field")

    out = {}
    for offset, width, key, signed in fields:
        raw = (value >> offset) & ((1 << width) - 1)
        if signed and raw >= 1 << (width - 1):
            raw -= 1 << width
        out[key] = raw
    return out
