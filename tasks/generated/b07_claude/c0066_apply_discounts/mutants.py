[
    ("percent coupons all computed on the original subtotal (no compounding)", "            total -= (2 * total * c[\"value\"] + 100) // 200  # nearest cent, halves up", "            total -= (2 * subtotal * c[\"value\"] + 100) // 200  # nearest cent, halves up"),
    ("fixed coupon's nominal value not capped at the subtotal", "    return min(coupon[\"value\"], subtotal) * 100", "    return coupon[\"value\"] * 100"),
    ("group ties go to the later coupon", "_nominal(c, subtotal) > _nominal(coupons[best[group]], subtotal)", "_nominal(c, subtotal) >= _nominal(coupons[best[group]], subtotal)"),
]
