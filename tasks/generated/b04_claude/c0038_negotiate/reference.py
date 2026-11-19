import re

_TOKEN = re.compile(r"[A-Za-z0-9!#$%&'*+.^_`|~-]+")
_QVALUE = re.compile(r"0(\.[0-9]{0,3})?|1(\.0{0,3})?")
_OWS = " \t"


def _qvalue(text: str) -> int:
    """q as an integer number of thousandths (exact; no float rounding)."""
    if not _QVALUE.fullmatch(text):
        raise ValueError(f"bad q value: {text!r}")
    whole, _, frac = text.partition(".")
    return int(whole) * 1000 + int((frac + "000")[:3])


def _parse(accept: str) -> list[tuple[str, str, int]]:
    ranges = []
    for element in accept.split(","):
        element = element.strip(_OWS)
        if not element:
            continue
        media, *params = element.split(";")
        mtype, slash, subtype = media.strip(_OWS).partition("/")
        if not slash or not _TOKEN.fullmatch(mtype) or not _TOKEN.fullmatch(subtype):
            raise ValueError(f"bad media range: {media!r}")
        if mtype == "*" and subtype != "*":
            raise ValueError(f"bad media range: {media!r}")
        q = None
        for param in params:
            name, eq, value = param.strip(_OWS).partition("=")
            if not eq or not _TOKEN.fullmatch(name) or not _TOKEN.fullmatch(value):
                raise ValueError(f"bad parameter: {param!r}")
            if name.lower() == "q":
                if q is not None:
                    raise ValueError("duplicate q parameter")
                q = _qvalue(value)
        ranges.append((mtype.lower(), subtype.lower(), 1000 if q is None else q))
    return ranges or [("*", "*", 1000)]


def negotiate(accept: str, offered: list[str]) -> str | None:
    ranges = _parse(accept)
    best, best_q = None, 0
    for item in offered:
        otype, _, osub = item.lower().partition("/")
        by_kind: dict[int, int] = {}  # 2 = exact, 1 = type/*, 0 = */*
        for rtype, rsub, q in ranges:
            if rtype == otype and rsub == osub:
                kind = 2
            elif rtype == otype and rsub == "*":
                kind = 1
            elif rtype == "*":
                kind = 0
            else:
                continue
            by_kind[kind] = max(by_kind.get(kind, 0), q)
        quality = by_kind[max(by_kind)] if by_kind else 0
        if quality > best_q:
            best, best_q = item, quality
    return best
