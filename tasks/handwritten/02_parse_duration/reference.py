import re

_FULL = re.compile(r"(?:[0-9]+[dhms] *)+")
_TOKEN = re.compile(r"([0-9]+)([dhms])")
_SECONDS = {"d": 86400, "h": 3600, "m": 60, "s": 1}


def parse_duration(text: str) -> int:
    s = text.strip(" ")
    if not _FULL.fullmatch(s):
        raise ValueError(f"invalid duration: {text!r}")
    total, last = 0, -1
    for num, unit in _TOKEN.findall(s):
        idx = "dhms".index(unit)
        if idx <= last:
            raise ValueError("repeated or out-of-order unit")
        last = idx
        total += int(num) * _SECONDS[unit]
    return total
