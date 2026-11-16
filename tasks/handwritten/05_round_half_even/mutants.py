[
    ("uses binary floats", "    value = Decimal(number)\n", "    return format(round(float(number), places), f\".{places}f\")\n    value = Decimal(number)\n"),
    ("rounds half up instead of half to even", "rounding=ROUND_HALF_EVEN", "rounding=\"ROUND_HALF_UP\""),
    ("keeps the minus sign on a zero result", "        rounded = abs(rounded)  # drop the sign of negative zero", "        pass"),
]
