import re

_PERCENT = re.compile(r"(100|[0-9]{1,2})(?:\.([0-9]{1,2}))?")


def _fnv1a32(data: bytes) -> int:
    h = 0x811C9DC5
    for b in data:
        h ^= b  # FNV-1a: XOR first, then multiply
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def rollout_bucket(flag: str, user_id: str, percent: str) -> tuple[int, bool]:
    m = _PERCENT.fullmatch(percent)
    if not m:
        raise ValueError(f"bad percent: {percent!r}")
    basis_points = int(m.group(1)) * 100 + int((m.group(2) or "0").ljust(2, "0"))
    if basis_points > 10000:
        raise ValueError(f"percent above 100: {percent!r}")
    bucket = _fnv1a32(f"{flag}:{user_id}".encode("utf-8")) % 10000
    return bucket, bucket < basis_points
