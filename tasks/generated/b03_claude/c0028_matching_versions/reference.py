import re

_NUM = r"(?:0|[1-9][0-9]*)"
_VERSION = re.compile(rf"{_NUM}\.{_NUM}\.{_NUM}")
_COMPARATOR = re.compile(rf"(>=|<=|>|<|=)?({_NUM}(?:\.{_NUM}){{0,2}})")


def _parse_version(v: str) -> tuple[int, ...]:
    if not isinstance(v, str) or not _VERSION.fullmatch(v):
        raise ValueError(f"malformed version: {v!r}")
    return tuple(int(x) for x in v.split("."))


def _parse_range(spec: str):
    alternatives = []
    for alt in spec.split("||"):
        tokens = alt.split()
        if not tokens:
            raise ValueError("empty alternative")
        if tokens == ["*"]:
            alternatives.append([])
            continue
        comparators = []
        for tok in tokens:
            m = _COMPARATOR.fullmatch(tok)
            if not m:
                raise ValueError(f"malformed comparator: {tok!r}")
            comparators.append((m.group(1) or "=", tuple(int(x) for x in m.group(2).split("."))))
        alternatives.append(comparators)
    return alternatives


def _holds(version: tuple[int, ...], op: str, parts: tuple[int, ...]) -> bool:
    prefix = version[: len(parts)]  # partial comparators look at the first k parts only
    return {
        "=": prefix == parts,
        ">": prefix > parts,
        ">=": prefix >= parts,
        "<": prefix < parts,
        "<=": prefix <= parts,
    }[op]


def matching_versions(versions: list[str], spec: str) -> list[str]:
    parsed = [_parse_version(v) for v in versions]
    alternatives = _parse_range(spec)
    return [
        v for v, pv in zip(versions, parsed)
        if any(all(_holds(pv, op, parts) for op, parts in alt) for alt in alternatives)
    ]
