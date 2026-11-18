import ipaddress
import random

import pytest
from solution import compress_ipv6


@pytest.mark.parametrize(
    "addr, expected",
    [
        ("2001:0DB8:0000:0000:0000:ff00:0042:8329", "2001:db8::ff00:42:8329"),
        ("1:0:0:2:0:0:3:4", "1::2:0:0:3:4"),
        ("0:0:0:0:0:0:0:0", "::"),
        ("::", "::"),
        ("::1", "::1"),
        ("1::", "1::"),
        ("2001:db8:0:1:0:0:0:1", "2001:db8:0:1::1"),
        ("2001:db8:0:1:1:1:1:1", "2001:db8:0:1:1:1:1:1"),
        ("1:2:3:4:5:6:7::", "1:2:3:4:5:6:7:0"),
        ("::2:3:4:5:6:7:8", "0:2:3:4:5:6:7:8"),
        ("1:0:0:0:2:0:0:0", "1::2:0:0:0"),
        ("0:0:1:0:0:0:1:0", "0:0:1::1:0"),
        ("ABCD:EF01:2345:6789:ABCD:EF01:2345:6789", "abcd:ef01:2345:6789:abcd:ef01:2345:6789"),
        ("fe80::0:0:1", "fe80::1"),
        ("0001:0:0:0:0:0:0:0001", "1::1"),
    ],
)
def test_examples(addr, expected):
    assert compress_ipv6(addr) == expected


@pytest.mark.parametrize(
    "addr",
    ["", ":", ":::", "1::2::3", "1:2:3:4:5:6:7:8::", "::1:2:3:4:5:6:7:8", "1:2:3:4:5:6:7", "1:2:3:4:5:6:7:8:9",
     "12345::", "g::1", "1:2:3:4:5:6:7:", ":1:2:3:4:5:6:7", "::1.2.3.4", "fe80::1%eth0", " ::1", "1:2:3:4:5:6::7:8"],
)
def test_invalid(addr):
    with pytest.raises(ValueError):
        compress_ipv6(addr)


def test_random_against_ipaddress():
    rng = random.Random(82)
    for _ in range(300):
        vals = [rng.choice([0, 0, 0, 1, 0xFF, rng.randrange(65536)]) for _ in range(8)]
        full = ":".join(format(v, rng.choice(["x", "04x", "X"])) for v in vals)
        assert compress_ipv6(full) == ipaddress.IPv6Address(full).compressed, full
