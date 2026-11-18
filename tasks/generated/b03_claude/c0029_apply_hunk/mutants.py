[
    ("B == 0 insertion placed before line A instead of after it", "start = a - 1 if b > 0 else a  # B == 0: insert after line A", "start = a - 1 if b > 0 else max(a - 1, 0)"),
    ("header line counts not checked", "    if len(old) != b or len(new) != d:", "    if len(old) != b:"),
    ("old lines not verified against the file", "    if start < 0 or lines[start : start + b] != old:", "    if start < 0:"),
]
