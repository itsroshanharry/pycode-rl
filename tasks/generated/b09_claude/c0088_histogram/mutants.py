[
    ("floating point instead of exact decimals", "    return Fraction(s)  # exact decimal value; float(\"0.3\") / 0.1 would be 2.9999999999999996", "    return float(s)"),
    ("hi itself counted as overflow (last bin right-open)", "        elif x > b:", "        elif x >= b:"),
    ("bin count rounded down instead of up", "    n = -((-span.numerator) // span.denominator)  # ceil", "    n = max(1, span.numerator // span.denominator)"),
]
