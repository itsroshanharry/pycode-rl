def allocate_orders(orders: list[tuple[str, int, str, int]],
                    warehouses: list[tuple[str, dict[str, int]]]) -> list[tuple[str, list[tuple[str, int]], int]]:
    if len({o[0] for o in orders}) != len(orders) or any(o[3] < 1 for o in orders):
        raise ValueError("duplicate order id or qty < 1")
    if len({w[0] for w in warehouses}) != len(warehouses):
        raise ValueError("duplicate warehouse")
    stock = []
    for name, levels in warehouses:
        if any(v < 0 for v in levels.values()):
            raise ValueError(f"negative stock in {name!r}")
        stock.append((name, dict(levels)))

    # Stable sort: equal priorities keep their input order.
    processing = sorted(range(len(orders)), key=lambda i: -orders[i][1])
    results: list = [None] * len(orders)
    for i in processing:
        order_id, _, sku, qty = orders[i]
        need, taken = qty, []
        for name, levels in stock:
            if need == 0:
                break
            take = min(need, levels.get(sku, 0))
            if take > 0:
                levels[sku] -= take
                need -= take
                taken.append((name, take))
        results[i] = (order_id, taken, need)
    return results  # original order of `orders`
