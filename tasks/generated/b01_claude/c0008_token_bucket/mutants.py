[
    ("bucket starts empty", "    tokens = Fraction(capacity)\n", "    tokens = Fraction(0)\n"),
    ("refill not capped at capacity", "tokens = min(Fraction(capacity), tokens + Fraction(rate * (t - last), 1000))", "tokens = tokens + Fraction(rate * (t - last), 1000)"),
    ("exactly enough tokens is rejected", "if tokens >= cost:", "if tokens > cost:"),
]
