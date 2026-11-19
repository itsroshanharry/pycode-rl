[
    ("remainder ties broken by position only (weight ignored)", "key=lambda i: (-remainders[i], -weights[i], i)", "key=lambda i: (-remainders[i], i)"),
    ("negative totals floored directly instead of mirrored", "    if total < 0:\n        return [-p for p in allocate_cents(-total, weights)]\n", ""),
    ("left-over cents go to the smallest remainders", "key=lambda i: (-remainders[i], -weights[i], i)", "key=lambda i: (remainders[i], -weights[i], i)"),
]
