import re

_OCTET = r"(0|[1-9][0-9]{0,2})"
_BLOCK = re.compile(rf"{_OCTET}\.{_OCTET}\.{_OCTET}\.{_OCTET}/(0|[1-9][0-9]?)")


def _parse(block: str) -> tuple[int, int]:
    m = _BLOCK.fullmatch(block)
    if not m:
        raise ValueError(f"malformed CIDR block: {block!r}")
    octets = [int(x) for x in m.groups()[:4]]
    prefix = int(m.group(5))
    if any(o > 255 for o in octets) or prefix > 32:
        raise ValueError(f"malformed CIDR block: {block!r}")
    addr = (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]
    size = 1 << (32 - prefix)
    start = addr & ~(size - 1) & 0xFFFFFFFF
    return start, start + size - 1


def _format(addr: int, prefix: int) -> str:
    return ".".join(str((addr >> shift) & 255) for shift in (24, 16, 8, 0)) + f"/{prefix}"


def merge_cidrs(blocks: list[str]) -> list[str]:
    merged: list[list[int]] = []
    for lo, hi in sorted(_parse(b) for b in blocks):
        if merged and lo <= merged[-1][1] + 1:  # overlapping or touching
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    out = []
    for lo, hi in merged:
        # Greedy: the largest aligned block starting at lo that fits is always optimal.
        while lo <= hi:
            size = lo & -lo if lo else 1 << 32
            while size > hi - lo + 1:
                size >>= 1
            out.append(_format(lo, 33 - size.bit_length()))
            lo += size
    return out
