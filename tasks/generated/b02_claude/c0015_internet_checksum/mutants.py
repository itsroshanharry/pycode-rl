[
    ("little-endian words", "total += (data[i] << 8) | data[i + 1]", "total += data[i] | (data[i + 1] << 8)"),
    ("carry discarded instead of wrapped around", "total = (total & 0xFFFF) + (total >> 16)", "total = total & 0xFFFF"),
    ("odd length padded at the front", 'data = data + b"\\x00"', 'data = b"\\x00" + data'),
]
