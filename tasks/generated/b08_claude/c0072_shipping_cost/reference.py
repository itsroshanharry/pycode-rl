def shipping_cost(weight_g: int, dims_cm: tuple[int, int, int], zone: str, subtotal: int,
                  rates: dict[str, list[tuple[int, int]]], free_over: dict[str, int]) -> int:
    length, width, height = dims_cm
    if weight_g < 1 or min(length, width, height) < 1 or zone not in rates:
        raise ValueError("bad parcel or zone")
    dim_weight = -(-(length * width * height) // 5)  # ceil(volume / 5) grams
    billable = max(weight_g, dim_weight)
    billable = -(-billable // 500) * 500  # round up to a multiple of 500 g
    for max_grams, price in rates[zone]:
        if billable <= max_grams:
            break
    else:
        raise ValueError("parcel too heavy for this zone")
    if zone in free_over and subtotal >= free_over[zone]:
        return 0
    return price
