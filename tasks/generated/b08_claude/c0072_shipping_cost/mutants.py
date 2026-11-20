[
    ("dimensional weight rounded down", "    dim_weight = -(-(length * width * height) // 5)  # ceil(volume / 5) grams", "    dim_weight = (length * width * height) // 5"),
    ("exact multiples of 500 g bumped to the next step", "    billable = -(-billable // 500) * 500  # round up to a multiple of 500 g", "    billable = (billable // 500 + 1) * 500"),
    ("free shipping only strictly above the threshold", "    if zone in free_over and subtotal >= free_over[zone]:", "    if zone in free_over and subtotal > free_over[zone]:"),
]
