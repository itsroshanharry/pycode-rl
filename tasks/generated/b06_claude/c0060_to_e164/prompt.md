```python
def to_e164(raw: str, default_cc: str, trunk_prefix: str) -> str:
    """Normalize a phone number to E.164: "+" followed by 8 to 15 digits.

    `raw` may contain only ASCII digits, the separators space, "-", "." "(" and
    ")", and a "+" as its very first character. Anything else (letters,
    extensions, a "+" elsewhere, non-ASCII digits) is a ValueError.
    `default_cc` is the country code to use for national numbers (1-3 ASCII
    digits, not starting with "0"); `trunk_prefix` is the national trunk
    prefix ("" or ASCII digits, e.g. "0" in the UK, "1" in the US, "8" in
    Russia, "" for countries that keep the leading 0).

    1. If raw starts with "+", it is international: first remove every "(0)"
       (the optional trunk zero written as in "+44 (0)20 ..."), then drop all
       separators; the digits are the full number.
    2. Otherwise drop all separators. If the digits start with "00" (the
       international call prefix), drop those two zeros; the rest is the full
       number.
    3. Otherwise it is national: if trunk_prefix is not empty and the digits
       start with it, remove it ONCE; then put default_cc in front.
    The resulting digits must be 8 to 15 long and must not start with "0";
    return "+" + digits. Raise ValueError otherwise.

    >>> to_e164("+44 (0)20 7946 0958", "1", "1")
    '+442079460958'
    >>> to_e164("(415) 555-0100", "1", "1")
    '+14155550100'
    """
```
