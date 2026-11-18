[
    ("interest truncated instead of rounded half-up", "    return math.floor(x + Fraction(1, 2))", "    return math.floor(x)"),
    ("final month not adjusted to clear the balance", "        if month == months:", "        if False:"),
    ("zero-rate payment divides by months + 1", "payment = _half_up(Fraction(principal_cents, months))", "payment = _half_up(Fraction(principal_cents, months + 1))"),
]
