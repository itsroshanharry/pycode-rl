def internet_checksum(data: bytes) -> int:
    if len(data) % 2:
        data = data + b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i + 1]
        while total > 0xFFFF:
            total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF
