[
    ("lowest priority processed first", "    processing = sorted(range(len(orders)), key=lambda i: -orders[i][1])", "    processing = sorted(range(len(orders)), key=lambda i: orders[i][1])"),
    ("results returned in processing order", "    return results  # original order of `orders`", "    return [results[i] for i in processing]"),
    ("warehouses with nothing taken are listed too", "            if take > 0:\n                levels[sku] -= take\n                need -= take\n                taken.append((name, take))", "            if sku in levels:\n                levels[sku] -= take\n                need -= take\n                taken.append((name, take))"),
]
