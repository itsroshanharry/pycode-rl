def _round_half_away(num: int, den: int) -> int:
    """num / den to the nearest integer, halves away from zero (den > 0)."""
    q = (2 * abs(num) + den) // (2 * den)
    return q if num >= 0 else -q


def invoice_tax_diff(lines: list[int], rate_bp: int) -> tuple[int, int, int]:
    if rate_bp < 0:
        raise ValueError("rate must be >= 0")
    per_line = sum(_round_half_away(n * rate_bp, 10000) for n in lines)
    per_invoice = _round_half_away(sum(lines) * rate_bp, 10000)
    return per_line, per_invoice, per_line - per_invoice
