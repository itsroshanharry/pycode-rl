[
    ("short form padded with 0 instead of doubling", '        digits = "".join(c * 2 for c in digits)', '        digits = "".join("0" + c for c in digits)'),
    ("missing alpha defaults to transparent", '        digits += "ff"', '        digits += "00"'),
    ("4-digit #RGBA form rejected", "len(text) not in (4, 5, 7, 9)", "len(text) not in (4, 7, 9)"),
]
