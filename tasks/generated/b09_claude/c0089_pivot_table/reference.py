def pivot_table(triples: list[tuple[str, str, int]], policy: str, default: int, totals: bool) -> list[list]:
    if policy not in ("sum", "max", "first", "last", "error"):
        raise ValueError(f"unknown policy {policy!r}")
    cells: dict[tuple[str, str], int] = {}
    for row, col, value in triples:
        key = (row, col)
        if key not in cells:
            cells[key] = value
        elif policy == "sum":
            cells[key] += value
        elif policy == "max":
            cells[key] = max(cells[key], value)
        elif policy == "last":
            cells[key] = value
        elif policy == "error":
            raise ValueError(f"duplicate cell {key}")
        # "first": keep what is there
    rows = sorted({r for r, _ in cells})
    cols = sorted({c for _, c in cells})
    table: list[list] = [[""] + cols + (["Total"] if totals else [])]
    col_totals = [0] * len(cols)
    for r in rows:
        line: list = [r]
        row_total = 0
        for j, c in enumerate(cols):
            v = cells.get((r, c))
            line.append(default if v is None else v)
            if v is not None:  # default cells count as 0 in totals
                row_total += v
                col_totals[j] += v
        if totals:
            line.append(row_total)
        table.append(line)
    if totals:
        table.append(["Total"] + col_totals + [sum(col_totals)])
    return table
