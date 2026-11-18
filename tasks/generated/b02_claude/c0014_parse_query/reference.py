_HEX = "0123456789abcdefABCDEF"


def _decode(s: str) -> str:
    buf = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == "+":
            buf += b" "
            i += 1
        elif c == "%":
            h = s[i + 1 : i + 3]
            if len(h) != 2 or any(ch not in _HEX for ch in h):
                raise ValueError(f"bad percent escape at position {i}")
            buf.append(int(h, 16))
            i += 3
        else:
            buf += c.encode("utf-8")
            i += 1
    try:
        return buf.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("decoded bytes are not valid UTF-8") from None


def parse_query(query: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for segment in query.split("&"):
        if not segment:
            continue
        raw_key, _, raw_value = segment.partition("=")
        key = _decode(raw_key)
        if not key:
            raise ValueError("empty key")
        out.setdefault(key, []).append(_decode(raw_value))
    return out
