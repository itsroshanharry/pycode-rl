def allocate_cents(total: int, weights: list[int]) -> list[int]:
    if not weights or any(w < 0 for w in weights) or sum(weights) == 0:
        raise ValueError("weights must be non-negative with a positive sum")
    if total < 0:
        return [-p for p in allocate_cents(-total, weights)]
    whole = sum(weights)
    # Integer arithmetic only: share = total*w/whole = floor + remainder/whole.
    parts = [total * w // whole for w in weights]
    remainders = [total * w % whole for w in weights]
    left = total - sum(parts)
    order = sorted(range(len(weights)), key=lambda i: (-remainders[i], -weights[i], i))
    for i in order[:left]:
        parts[i] += 1
    return parts
