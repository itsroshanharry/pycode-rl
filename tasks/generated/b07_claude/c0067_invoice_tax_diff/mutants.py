[
    ("halves rounded up toward +infinity (wrong for credits)", "    q = (2 * abs(num) + den) // (2 * den)\n    return q if num >= 0 else -q", "    return (2 * num + den) // (2 * den)"),
    ("halves rounded toward zero", "    q = (2 * abs(num) + den) // (2 * den)", "    q = (2 * abs(num) + den - 1) // (2 * den)"),
    ("difference reported the other way round", "    return per_line, per_invoice, per_line - per_invoice", "    return per_line, per_invoice, per_invoice - per_line"),
]
