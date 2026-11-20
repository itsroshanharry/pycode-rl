[
    ("exponent applied to the unit only, not to the prefix (cm^2 read as c * m^2)", "        scale *= (p * s) ** exp  # the exponent applies to the prefixed unit", "        scale *= p * s ** exp"),
    ("everything after the first '/' is in the denominator (a/b*c read as a/(b*c))", "        if op == \"/\":\n            exp = -exp  # \"/\" inverts only this one factor (left-to-right evaluation)", "        if op == \"/\" or \"/\" in parts[:k]:\n            exp = -exp"),
    ("ties rounded half up", "    if rest > Fraction(1, 2) or (rest == Fraction(1, 2) and q % 2):", "    if rest >= Fraction(1, 2):"),
]
