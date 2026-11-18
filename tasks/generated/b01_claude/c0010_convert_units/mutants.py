[
    ("reverse direction uses the factor instead of its inverse", "graph.setdefault(b, []).append((a, 1 / r))", "graph.setdefault(b, []).append((a, r))"),
    ("whole numbers formatted as p/1", 'return str(result.numerator) if result.denominator == 1 else f"{result.numerator}/{result.denominator}"', 'return f"{result.numerator}/{result.denominator}"'),
    ("negative amounts rejected", "value = _number(amount, allow_negative=True)", "value = _number(amount, allow_negative=False)"),
]
