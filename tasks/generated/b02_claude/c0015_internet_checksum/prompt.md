```python
def internet_checksum(data: bytes) -> int:
    """16-bit one's-complement checksum of a byte string (as used in IPv4 headers).

    Split `data` into 16-bit big-endian words (first byte is the high byte); if the
    length is odd, append one zero byte first. Add up all words; whenever the
    running sum no longer fits in 16 bits, add the part above the low 16 bits back
    into the low 16 bits ("end-around carry"), until it fits. Return the bitwise
    complement of the final 16-bit sum, as an int in 0..65535. Empty data gives
    65535.

    >>> internet_checksum(bytes([0x00, 0x01, 0xF2, 0x03, 0xF4, 0xF5, 0xF6, 0xF7]))
    8717
    >>> internet_checksum(b"")
    65535
    """
```
