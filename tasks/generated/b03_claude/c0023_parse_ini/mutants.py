[
    ("keys kept case-sensitive", "key = key.strip().lower()", "key = key.strip()"),
    ("any ';' or '#' starts a comment", '_INLINE = re.compile(r"\\s[;#]")', '_INLINE = re.compile(r"[;#]")'),
    ("value split at the last '='", 'key, sep, value = line.partition("=")', 'key, sep, value = line.rpartition("=")'),
]
