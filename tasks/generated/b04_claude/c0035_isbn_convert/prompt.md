```python
def isbn_convert(isbn: str) -> str:
    """Convert an ISBN-10 to ISBN-13 or an ISBN-13 to ISBN-10.

    Hyphens and spaces in the input are ignored; nothing else is. "Digit" always
    means an ASCII digit 0-9 (other Unicode digits are invalid characters).
    - ISBN-10: 9 digits and a check character (a digit, or "X"/"x" meaning 10). It is
      valid if sum(d_i * w_i) over all 10 positions, with weights 10, 9, ..., 1, is
      divisible by 11. Convert it by taking "978" + its first 9 digits and appending
      the ISBN-13 check digit.
    - ISBN-13: 13 digits, valid if sum(d_i * w_i) with weights 1, 3, 1, 3, ... is
      divisible by 10. Only ISBNs starting with "978" can be converted: take digits
      4 to 12 (the 9 after "978") and append the ISBN-10 check character.
    Return just the digits of the result (and a final uppercase "X" if the ISBN-10
    check value is 10).
    Raise ValueError for a wrong length, an invalid character (including "X" anywhere
    but the last position of a 10-character ISBN), a failed check, or an ISBN-13 that
    does not start with "978".

    >>> isbn_convert("0-306-40615-2")
    '9780306406157'
    >>> isbn_convert("978 0 306 40615 7")
    '0306406152'
    """
```
