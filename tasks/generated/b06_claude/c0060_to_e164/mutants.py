[
    ("the '(0)' trunk marker kept in international numbers", "        digits = _digits(raw[1:].replace(\"(0)\", \"\"))", "        digits = _digits(raw[1:])"),
    ("international prefix 00 treated as one zero", "            digits = digits[2:]  # international call prefix", "            digits = digits[1:]  # international call prefix"),
    ("trunk prefix stripped repeatedly", "                digits = digits[len(trunk_prefix):]  # once, not lstrip", "                digits = digits.lstrip(trunk_prefix)"),
]
