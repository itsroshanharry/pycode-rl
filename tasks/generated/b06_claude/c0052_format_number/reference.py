import re

_NUM = re.compile(r"(-?)([0-9]+)(?:\.([0-9]+))?")


def _group(int_s: str, grouping: list[int], sep: str) -> str:
    if not grouping:
        return int_s
    parts, rest, k = [], int_s, 0
    while True:
        size = grouping[min(k, len(grouping) - 1)]  # the last size repeats
        if len(rest) <= size:
            break
        parts.append(rest[-size:])
        rest = rest[:-size]
        k += 1
    parts.append(rest)
    return sep.join(reversed(parts))


def format_number(value: str, decimal_mark: str, group_sep: str, grouping: list[int], frac_digits: int) -> str:
    m = _NUM.fullmatch(value)
    if not m:
        raise ValueError(f"bad number: {value!r}")
    if frac_digits < 0 or any(g < 1 for g in grouping):
        raise ValueError("bad frac_digits or grouping")
    if not decimal_mark or not group_sep or decimal_mark == group_sep:
        raise ValueError("bad decimal mark / group separator")
    negative, int_part, frac = m.group(1) == "-", m.group(2), m.group(3) or ""

    # Exact integer arithmetic (no float, no Decimal context precision limits).
    scaled, n = int(int_part + frac), len(frac)  # |value| * 10**n
    if frac_digits >= n:
        q = scaled * 10 ** (frac_digits - n)
    else:
        unit = 10 ** (n - frac_digits)
        q, rem = divmod(scaled, unit)
        if 2 * rem > unit:
            q += 1
        elif 2 * rem == unit and q % 2:
            q += 1  # tie: round to the even last digit

    digits = str(q).rjust(frac_digits + 1, "0")
    int_s = digits[: len(digits) - frac_digits]
    frac_s = digits[len(digits) - frac_digits:]
    sign = "-" if negative and q else ""
    out = sign + _group(int_s, grouping, group_sep)
    return out + decimal_mark + frac_s if frac_digits else out
