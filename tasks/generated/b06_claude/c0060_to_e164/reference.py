import re

_SEPARATORS = " -.()"
_ALLOWED = set("0123456789" + _SEPARATORS)


def _digits(text: str) -> str:
    if not set(text) <= _ALLOWED:
        raise ValueError(f"unexpected character in {text!r}")
    return "".join(c for c in text if c.isascii() and c.isdigit())


def to_e164(raw: str, default_cc: str, trunk_prefix: str) -> str:
    if not re.fullmatch(r"[1-9][0-9]{0,2}", default_cc) or not re.fullmatch(r"[0-9]*", trunk_prefix):
        raise ValueError("bad default_cc or trunk_prefix")
    if raw.startswith("+"):
        digits = _digits(raw[1:].replace("(0)", ""))
    else:
        digits = _digits(raw)
        if digits.startswith("00"):
            digits = digits[2:]  # international call prefix
        else:
            if trunk_prefix and digits.startswith(trunk_prefix):
                digits = digits[len(trunk_prefix):]  # once, not lstrip
            digits = default_cc + digits
    if not 8 <= len(digits) <= 15 or digits.startswith("0"):
        raise ValueError(f"not a valid E.164 number: {raw!r}")
    return "+" + digits
