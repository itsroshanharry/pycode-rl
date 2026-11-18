```python
def merge_cidrs(blocks: list[str]) -> list[str]:
    """Return the fewest IPv4 CIDR blocks that cover exactly the same addresses.

    Each input is "a.b.c.d/p": four decimal octets 0..255 written without leading
    zeros (except "0" itself), and a prefix length p in 0..32, also without leading
    zeros. Bits after the prefix may be anything ("10.0.0.5/24" means the block
    10.0.0.0/24). Inputs may overlap, nest, repeat or touch.
    Output blocks are canonical (bits after the prefix are zero), do not overlap,
    are sorted by network address, and their union is exactly the union of the
    inputs, using as few blocks as possible.
    Raise ValueError for any malformed block (no surrounding spaces allowed).

    >>> merge_cidrs(["10.0.0.0/25", "10.0.0.128/25", "10.0.1.0/24"])
    ['10.0.0.0/23']
    >>> merge_cidrs(["192.168.1.7/32", "192.168.1.0/24"])
    ['192.168.1.0/24']
    """
```
