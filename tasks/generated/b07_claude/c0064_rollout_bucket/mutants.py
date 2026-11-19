[
    ("FNV-1 order (multiply, then XOR)", "        h ^= b  # FNV-1a: XOR first, then multiply\n        h = (h * 0x01000193) & 0xFFFFFFFF", "        h = (h * 0x01000193) & 0xFFFFFFFF\n        h ^= b"),
    ("hashes code points instead of UTF-8 bytes", "    bucket = _fnv1a32(f\"{flag}:{user_id}\".encode(\"utf-8\")) % 10000", "    bucket = _fnv1a32([ord(c) & 0xFF for c in f\"{flag}:{user_id}\"]) % 10000"),
    ("bucket equal to the threshold included", "    return bucket, bucket < basis_points", "    return bucket, bucket <= basis_points"),
]
