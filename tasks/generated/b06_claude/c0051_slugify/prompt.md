```python
def slugify(title: str, translit: dict[str, str], max_len: int) -> str:
    """Make a URL slug from a title.

    Steps, in this order:
    1. Replace every character of `title` that is a key of `translit` by its
       value (keys are single characters, matched exactly, case-sensitively,
       against the ORIGINAL title; replacements are not re-translated).
    2. Lowercase the ASCII letters A-Z. No other character is changed.
    3. The words are the maximal runs of ASCII a-z and 0-9; every other
       character (including any non-ASCII character still present) is a
       separator. Join the words with "-".
    4. If the slug is longer than `max_len`, keep the longest prefix made of
       whole words that fits; if even the first word does not fit, cut the
       first word to `max_len` characters.
    A title with no words gives "". Raise ValueError if max_len < 1.

    >>> slugify("Grüße aus Köln!", {"ü": "ue", "ß": "ss", "ö": "oe"}, 50)
    'gruesse-aus-koeln'
    >>> slugify("The quick brown fox", {}, 14)
    'the-quick'
    """
```
