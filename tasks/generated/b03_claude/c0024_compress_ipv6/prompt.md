```python
def compress_ipv6(addr: str) -> str:
    """Return the canonical (RFC 5952) text form of an IPv6 address.

    Input: 8 groups of 1 to 4 hex digits (either case) separated by ":"; or fewer
    groups with exactly one "::", which stands for one or more zero groups so that
    the total becomes 8 ("::" may be at the start, middle or end; "::" alone means
    all zeros). Nothing else is allowed (no spaces, no embedded IPv4 such as
    "::1.2.3.4", no zone suffix such as "%eth0").
    Output: lowercase; leading zeros removed from every group (a zero group is "0");
    the longest run of two or more consecutive zero groups replaced by "::"; if two
    runs are equally long, replace the leftmost one; a single zero group is never
    replaced by "::".
    Raise ValueError for malformed input, including more than one "::", a "::"
    together with 8 groups, an empty or too-long group, or a non-hex character.

    >>> compress_ipv6("2001:0DB8:0000:0000:0000:ff00:0042:8329")
    '2001:db8::ff00:42:8329'
    >>> compress_ipv6("1:0:0:2:0:0:3:4")
    '1::2:0:0:3:4'
    """
```
