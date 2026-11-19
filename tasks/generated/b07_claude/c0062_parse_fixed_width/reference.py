import re
from datetime import date

_INT = re.compile(r" *(-?)([0-9]+) *")


def _parse_int(text: str) -> tuple[bool, int] | None:
    if text.strip(" ") == "":
        return None
    m = _INT.fullmatch(text)
    if not m:
        raise ValueError(f"not an integer field: {text!r}")
    return m.group(1) == "-", int(m.group(2))


def parse_fixed_width(record: str, layout: list[tuple[str, int, int, str]]) -> dict:
    out: dict = {}
    for name, start, width, kind in layout:
        if start < 1 or width < 1 or name in out:
            raise ValueError(f"bad layout entry for {name!r}")
        lo = start - 1  # 1-based column -> 0-based index
        if len(record) < lo + width:
            raise ValueError("record too short")
        text = record[lo:lo + width]
        if kind == "str":
            value = text.rstrip(" ")
        elif kind == "int":
            parsed = _parse_int(text)
            value = None if parsed is None else (-parsed[1] if parsed[0] else parsed[1])
        elif kind == "cents":
            parsed = _parse_int(text)
            if parsed is None:
                value = None
            else:
                neg, n = parsed
                value = ("-" if neg and n else "") + f"{n // 100}.{n % 100:02d}"
        elif kind == "date":
            if text.strip(" ") == "" or text == "00000000":
                value = None
            elif width != 8 or not re.fullmatch(r"[0-9]{8}", text):
                raise ValueError(f"bad date field: {text!r}")
            else:
                value = date(int(text[:4]), int(text[4:6]), int(text[6:])).isoformat()
        elif kind == "flag":
            if width != 1 or text not in ("Y", "N", " "):
                raise ValueError(f"bad flag field: {text!r}")
            value = {"Y": True, "N": False, " ": None}[text]
        else:
            raise ValueError(f"unknown kind: {kind!r}")
        out[name] = value
    return out
