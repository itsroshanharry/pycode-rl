import re

_VERSION = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?"
)
_IDENT = re.compile(r"[0-9A-Za-z-]+")


def _key(v: str):
    m = _VERSION.fullmatch(v)
    if not m:
        raise ValueError(f"invalid version: {v!r}")
    major, minor, patch, pre, build = m.groups()
    for part in (pre, build):
        if part is not None and not all(_IDENT.fullmatch(i) for i in part.split(".")):
            raise ValueError(f"empty or invalid identifier: {v!r}")
    pre_key = []
    if pre is not None:
        for ident in pre.split("."):
            if ident.isdigit():
                if len(ident) > 1 and ident[0] == "0":
                    raise ValueError(f"leading zero in pre-release: {v!r}")
                pre_key.append((0, int(ident), ""))
            else:
                pre_key.append((1, 0, ident))
    has_no_pre = 0 if pre is not None else 1
    return (int(major), int(minor), int(patch), has_no_pre, pre_key)


def semver_sort(versions: list[str]) -> list[str]:
    keys = [_key(v) for v in versions]  # validate everything before sorting
    order = sorted(range(len(versions)), key=lambda i: keys[i])
    return [versions[i] for i in order]
