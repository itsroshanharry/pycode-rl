[
    ("nearest rounds .5 up instead of to the even index", "        idx = hi if frac > Fraction(1, 2) or (frac == Fraction(1, 2) and lo % 2) else lo  # .5 -> even index", "        idx = hi if frac >= Fraction(1, 2) else lo"),
    ("values not sorted first", "    xs = sorted(values)", "    xs = list(values)"),
    ("position uses n instead of n - 1", "    h = Fraction(len(xs) - 1) * Fraction(p) / 100", "    h = min(Fraction(len(xs)) * Fraction(p) / 100, Fraction(len(xs) - 1))"),
]
