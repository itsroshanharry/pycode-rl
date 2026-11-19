def income_tax(income: int, allowance: int, taper_threshold: int, bands: list[tuple[int | None, int]]) -> int:
    if min(income, allowance, taper_threshold) < 0 or not bands:
        raise ValueError("bad amounts or bands")
    for k, (width, rate) in enumerate(bands):
        last = k == len(bands) - 1
        if (width is None) != last or (width is not None and width < 1) or not 0 <= rate <= 100:
            raise ValueError(f"bad band {k}")
    effective = allowance
    if income > taper_threshold:
        effective = max(0, allowance - (income - taper_threshold) // 2)
    remaining = max(0, income - effective)
    hundredths = 0  # tax * 100, exact integer
    for width, rate in bands:
        part = remaining if width is None else min(remaining, width)
        hundredths += part * rate
        remaining -= part
        if remaining == 0:
            break
    return hundredths // 100  # round the total down once
