[
    ("runs of two encoded as repeat packets", "        if r >= 3:", "        if r >= 2:"),
    ("repeat runs capped at 127", "        while i + r < n and r < 128 and data[i + r] == data[i]:", "        while i + r < n and r < 127 and data[i + r] == data[i]:"),
    ("literal packets allowed to grow to 129 bytes (header 128 is a no-op)", "            if len(literal) == 128:", "            if len(literal) == 129:"),
]
