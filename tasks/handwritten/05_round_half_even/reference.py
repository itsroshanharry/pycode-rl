from decimal import ROUND_HALF_EVEN, Decimal, localcontext


def round_half_even(number: str, places: int) -> str:
    value = Decimal(number)
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as ctx:
        ctx.prec = len(number) + places + 5
        rounded = value.quantize(quantum, rounding=ROUND_HALF_EVEN)
    if rounded == 0:
        rounded = abs(rounded)  # drop the sign of negative zero
    return format(rounded, "f")
