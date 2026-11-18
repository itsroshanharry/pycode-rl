[
    ("remainder ties broken by input order instead of name", "key=lambda n: (-(total_cents * weights[n] % total_w), n))", "key=lambda n: -(total_cents * weights[n] % total_w))"),
    ("leftover cents go to the largest weight, not the largest remainder", "key=lambda n: (-(total_cents * weights[n] % total_w), n))", "key=lambda n: (-weights[n], n))"),
    ("zero weights accepted", "if type(w) is not int or w <= 0:", "if type(w) is not int or w < 0:"),
]
