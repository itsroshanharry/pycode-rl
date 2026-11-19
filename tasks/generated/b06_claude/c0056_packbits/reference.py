def packbits(data: bytes) -> bytes:
    out = bytearray()
    literal = bytearray()

    def end_literal() -> None:
        if literal:
            out.append(len(literal) - 1)
            out.extend(literal)
            literal.clear()

    i, n = 0, len(data)
    while i < n:
        r = 1
        while i + r < n and r < 128 and data[i + r] == data[i]:
            r += 1
        if r >= 3:
            end_literal()
            out.append(257 - r)
            out.append(data[i])
            i += r
        else:
            literal.append(data[i])
            i += 1
            if len(literal) == 128:
                end_literal()
    end_literal()
    return bytes(out)
