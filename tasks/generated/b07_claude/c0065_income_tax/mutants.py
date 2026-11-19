[
    ("taper reduction rounded up (every started 2)", "        effective = max(0, allowance - (income - taper_threshold) // 2)", "        effective = max(0, allowance - -(-(income - taper_threshold) // 2))"),
    ("each band rounded down separately", "        hundredths += part * rate", "        hundredths += part * rate // 100 * 100"),
    ("taper measured on income above threshold after the allowance", "        effective = max(0, allowance - (income - taper_threshold) // 2)", "        effective = max(0, allowance - max(0, income - allowance - taper_threshold) // 2)"),
]
