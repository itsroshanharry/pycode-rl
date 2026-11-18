```python
def parse_csv_line(line: str, delimiter: str = ",") -> list[str]:
    """Split one CSV record into its fields.

    Fields are separated by `delimiter`, a single character that is not a double
    quote, newline or carriage return (otherwise raise ValueError). `line` contains
    no newline. An empty line is a single empty field.

    A field whose first character is a double quote is quoted: it ends at the next
    double quote that is not immediately followed by another double quote. Inside
    it, two double quotes stand for one literal double quote, and the delimiter has
    no special meaning. Right after the closing quote there must be the delimiter
    or the end of the line.
    Any other field is unquoted: it runs up to the next delimiter, is taken verbatim
    (surrounding spaces are kept) and must not contain a double quote.

    Raise ValueError for a malformed line: an unterminated quoted field, any
    character other than the delimiter right after a closing quote, or a double
    quote inside an unquoted field.

    >>> parse_csv_line('a,"b,c",d')
    ['a', 'b,c', 'd']
    >>> parse_csv_line('"say ""hi""";;x', ";")
    ['say "hi"', '', 'x']
    """
```
