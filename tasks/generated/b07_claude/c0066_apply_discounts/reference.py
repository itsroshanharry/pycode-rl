def _nominal(coupon: dict, subtotal: int) -> int:
    """Nominal discount in hundredths of a cent, so percent and fixed compare exactly."""
    if coupon["kind"] == "percent":
        return subtotal * coupon["value"]
    return min(coupon["value"], subtotal) * 100


def apply_discounts(subtotal: int, coupons: list[dict]) -> tuple[int, list[str]]:
    if subtotal < 0:
        raise ValueError("negative subtotal")
    seen = set()
    for c in coupons:
        kind, value = c["kind"], c["value"]
        if c["code"] in seen:
            raise ValueError(f"duplicate code {c['code']!r}")
        seen.add(c["code"])
        if kind == "percent" and not 1 <= value <= 100 or kind == "fixed" and value < 1 or kind not in ("percent", "fixed"):
            raise ValueError(f"bad coupon {c['code']!r}")

    best: dict[str, int] = {}  # group -> index of the chosen coupon
    for i, c in enumerate(coupons):
        group = c.get("group")
        if group is not None and (group not in best or _nominal(c, subtotal) > _nominal(coupons[best[group]], subtotal)):
            best[group] = i
    used = [c for i, c in enumerate(coupons) if c.get("group") is None or best[c["group"]] == i]

    total, applied = subtotal, []
    for c in used:
        if c["kind"] == "percent":
            total -= (2 * total * c["value"] + 100) // 200  # nearest cent, halves up
            applied.append(c["code"])
    for c in used:
        if c["kind"] == "fixed":
            total = max(0, total - c["value"])
            applied.append(c["code"])
    return total, applied
