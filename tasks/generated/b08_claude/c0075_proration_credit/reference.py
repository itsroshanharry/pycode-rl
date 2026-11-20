import re
from datetime import date


def _parse(text: str) -> date:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text):
        raise ValueError(f"bad date: {text!r}")
    return date(int(text[:4]), int(text[5:7]), int(text[8:]))


def proration_credit(cycle_start: str, cycle_end: str, change_date: str, old_price: int, new_price: int) -> int:
    start, end, change = _parse(cycle_start), _parse(cycle_end), _parse(change_date)
    if not start < end or not start <= change < end or min(old_price, new_price) < 0:
        raise ValueError("bad cycle, change date or price")
    total_days = (end - start).days  # end is exclusive
    remaining = (end - change).days  # the change day itself is billed at the new price
    num, den = (new_price - old_price) * remaining, total_days
    q = (2 * abs(num) + den) // (2 * den)  # halves away from zero
    return q if num >= 0 else -q
