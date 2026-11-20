[
    ("default cells counted in the totals", "            if v is not None:  # default cells count as 0 in totals\n                row_total += v\n                col_totals[j] += v", "            row_total += default if v is None else v\n            col_totals[j] += default if v is None else v"),
    ("'first' and 'last' swapped", "        elif policy == \"last\":\n            cells[key] = value", "        elif policy == \"first\":\n            cells[key] = value"),
    ("labels kept in order of first appearance instead of sorted", "    rows = sorted({r for r, _ in cells})", "    rows = list(dict.fromkeys(r for r, _ in cells))"),
]
