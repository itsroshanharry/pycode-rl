# An explicit ASCII set, not int(x, 16): int() also accepts "_", "+", spaces and non-ASCII digits.
_HEX = frozenset("0123456789abcdefABCDEF")


def hex_color(text: str) -> str:
    if not text.startswith("#") or len(text) not in (4, 5, 7, 9) or not set(text[1:]) <= _HEX:
        raise ValueError(f"not a hex color: {text!r}")
    digits = text[1:].lower()
    if len(digits) in (3, 4):
        digits = "".join(c * 2 for c in digits)
    if len(digits) == 6:
        digits += "ff"
    return "#" + digits
