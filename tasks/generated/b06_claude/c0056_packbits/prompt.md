```python
def packbits(data: bytes) -> bytes:
    """Encode bytes with PackBits run-length encoding, following one exact rule.

    The output is a sequence of packets:
    - literal packet: a header byte n in 0..127, then the next n + 1 bytes
      copied as they are (1 to 128 bytes);
    - repeat packet: a header byte h in 129..255, then ONE byte that stands
      for 257 - h copies of itself (2 to 128 copies).
    (Header 128 is never produced.)

    Encode by scanning left to right. At position i, let r be the number of
    consecutive bytes equal to data[i] starting at i, counting at most 128.
    - If r >= 3: end the current literal packet (if any), emit a repeat packet
      for those r bytes, and continue at i + r.
    - Otherwise: append data[i] to the current literal packet and continue at
      i + 1; a literal packet that reaches 128 bytes is ended immediately.
    At the end, end the current literal packet (if any). So a run of exactly
    two equal bytes goes into a literal packet, and a run longer than 128 is
    split into repeat packets of 128 with the rest handled by the same rule.
    Return the result as `bytes`.

    >>> packbits(b"ABBBC")
    b'\\x00A\\xfeB\\x00C'
    >>> packbits(bytes([0xAA, 0xAA, 0xAA, 0x80, 0x00, 0x2A]))
    b'\\xfe\\xaa\\x02\\x80\\x00*'
    """
```
