[
    ("'+' kept literally instead of meaning a space", '            buf += b" "', '            buf += b"+"'),
    ("split on the last '=' instead of the first", 'raw_key, _, raw_value = segment.partition("=")', 'raw_key, _, raw_value = segment.rpartition("=")'),
    ("repeated keys overwrite earlier values", "out.setdefault(key, []).append(_decode(raw_value))", "out[key] = [_decode(raw_value)]"),
]
