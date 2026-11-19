```python
def hex_color(text: str) -> str:
    """Canonicalize a CSS hex color to the lowercase 8-digit form "#rrggbbaa".

    Accepted input: "#" followed by exactly 3, 4, 6 or 8 hex digits
    (ASCII 0-9, a-f, A-F). In the 3- and 4-digit forms (#RGB, #RGBA) every
    digit is doubled ("#f0a" means "#ff00aa"). A missing alpha means "ff".
    Nothing else is accepted: no surrounding whitespace, no missing "#",
    no "0x", no signs, underscores or non-ASCII characters.
    Raise ValueError for anything else.

    >>> hex_color("#F0A")
    '#ff00aaff'
    >>> hex_color("#11223380")
    '#11223380'
    """
```
