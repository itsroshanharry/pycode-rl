import re

_SHAPE = re.compile(r"[A-Z]{2}[0-9]{2}[A-Z0-9]*")


def check_iban(iban: str, lengths: dict[str, int]) -> str:
    s = iban.replace(" ", "")
    if not _SHAPE.fullmatch(s):
        return "format"
    country = s[:2]
    if country not in lengths:
        return "country"
    if len(s) != lengths[country]:
        return "length"
    rearranged = s[4:] + s[:4]
    digits = "".join(str(int(c, 36)) for c in rearranged)  # "A" -> 10 ... "Z" -> 35
    if int(digits) % 97 != 1:
        return "checksum"
    return "ok"
