def top_k_per_group(rows: list[tuple[str, str, int]], k: int) -> dict[str, list[str]]:
    if k < 0:
        raise ValueError("k must be >= 0")
    groups: dict[str, list[tuple[str, int]]] = {}
    for group, name, score in rows:
        groups.setdefault(group, []).append((name, score))
    out = {}
    for group, members in groups.items():
        ranked = sorted(members, key=lambda m: (-m[1], m[0]))  # stable for exact ties
        out[group] = [name for name, _ in ranked[:k]]
    return out
