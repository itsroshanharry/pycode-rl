def split_bill(total_cents: int, weights: dict[str, int]) -> dict[str, int]:
    if not weights:
        raise ValueError("no people to split between")
    for name, w in weights.items():
        if type(w) is not int or w <= 0:
            raise ValueError(f"weight for {name!r} must be a positive int")
    total_w = sum(weights.values())
    shares = {n: total_cents * w // total_w for n, w in weights.items()}
    left = total_cents - sum(shares.values())
    order = sorted(weights, key=lambda n: (-(total_cents * weights[n] % total_w), n))
    for n in order[:left]:
        shares[n] += 1
    return shares
