```python
def unpack_bits(value: int, layout: list[tuple[str, int, int]]) -> dict[str, int]:
    """Decode a packed non-negative integer into named bit fields.

    Each layout entry is (name, offset, width): the field is bits
    offset .. offset + width - 1 of `value`, where bit 0 is the least
    significant bit. A name ending in "!" marks a SIGNED field, read as a
    two's-complement number of `width` bits; the "!" is not part of the
    result key. All other fields are unsigned.

    Return a dict from key to field value, with keys inserted in order of
    increasing offset (not layout order).

    Raise ValueError if value < 0, an offset is negative, a width is < 1,
    two fields share any bit, a key is empty, two fields have the same key
    (after removing "!"), or `value` has a 1 bit that is not inside any field.

    >>> unpack_bits(0b11010110, [("mode", 0, 3), ("delta!", 3, 4), ("flag", 7, 1)])
    {'mode': 6, 'delta': -6, 'flag': 1}
    """
```
