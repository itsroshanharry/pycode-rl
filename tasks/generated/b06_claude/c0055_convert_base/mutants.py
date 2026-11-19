[
    ("minus sign dropped when the integer part is 0", "    nonzero = int_out != \"0\" or any(c != \"0\" for c in frac_out)", "    nonzero = int_out != \"0\""),
    ("digits above 9 printed in uppercase", "    return _DIGITS[d]", "    return _DIGITS[d].upper()"),
    ("digits checked against base 36 instead of the source base", "        if _VALUE[c] >= from_base:", "        if _VALUE[c] >= 36:"),
]
