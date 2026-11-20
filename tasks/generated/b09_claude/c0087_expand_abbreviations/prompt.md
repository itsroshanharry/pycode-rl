```python
def expand_abbreviations(text: str, abbrevs: dict[str, str]) -> str:
    """Expand abbreviations in a text, preserving capitalization.

    Tokens are the maximal runs of ASCII letters and "." characters; every other
    character is copied unchanged. Dictionary keys are compared
    case-insensitively (ASCII). For each token, the FIRST rule that applies wins:
    1. the whole token equals a key ("e.g.", "approx"): replace the token;
    2. the token ends with "." and the token without its last "." equals a key
       (a sentence-ending period after an abbreviation, as in "approx."):
       replace that part and keep the final ".";
    3. otherwise the token is left unchanged (no partial matches inside a token).
    Capitalization of the replacement, decided from the matched part of the token:
    - if it has at least 2 letters and all its letters are uppercase, the
      expansion is fully uppercased ("ASAP" -> "AS SOON AS POSSIBLE");
    - else if its first letter is uppercase, only the first character of the
      expansion is uppercased ("Approx" -> "Approximately");
    - else the expansion is used as written in the dictionary.

    >>> expand_abbreviations("Approx. 5 kg, e.g. apples; ASAP!", {"approx": "approximately", "e.g.": "for example", "asap": "as soon as possible"})
    'Approximately. 5 kg, for example apples; AS SOON AS POSSIBLE!'
    """
```
