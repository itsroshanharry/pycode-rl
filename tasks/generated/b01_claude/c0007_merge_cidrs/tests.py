import ipaddress
import random

import pytest
from solution import merge_cidrs


@pytest.mark.parametrize(
    "blocks, expected",
    [
        (["10.0.0.0/25", "10.0.0.128/25", "10.0.1.0/24"], ["10.0.0.0/23"]),
        (["192.168.1.7/32", "192.168.1.0/24"], ["192.168.1.0/24"]),
        ([], []),
        (["0.0.0.0/0", "10.0.0.0/8"], ["0.0.0.0/0"]),
        (["10.0.0.5/24"], ["10.0.0.0/24"]),
        (["10.0.0.0/24", "10.0.2.0/24"], ["10.0.0.0/24", "10.0.2.0/24"]),
        (["10.0.1.0/24", "10.0.2.0/24"], ["10.0.1.0/24", "10.0.2.0/24"]),
        (["10.0.0.0/32", "10.0.0.1/32", "10.0.0.2/32"], ["10.0.0.0/31", "10.0.0.2/32"]),
        (["10.0.0.1/32", "10.0.0.2/32"], ["10.0.0.1/32", "10.0.0.2/32"]),
        (["255.255.255.255/32", "255.255.255.254/32"], ["255.255.255.254/31"]),
        (["1.2.3.4/32", "1.2.3.4/32"], ["1.2.3.4/32"]),
        (["128.0.0.0/1", "0.0.0.0/1"], ["0.0.0.0/0"]),
        (["10.0.0.0/23", "10.0.1.0/24"], ["10.0.0.0/23"]),
        (["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24", "192.168.4.0/24"],
         ["192.168.0.0/22", "192.168.4.0/24"]),
        (["10.0.0.0/8", "9.255.255.255/32", "11.0.0.0/32"], ["9.255.255.255/32", "10.0.0.0/8", "11.0.0.0/32"]),
    ],
)
def test_examples(blocks, expected):
    assert list(merge_cidrs(blocks)) == expected


@pytest.mark.parametrize(
    "bad",
    ["10.0.0.0", "10.0.0.0/33", "256.0.0.0/8", "10.0.0/8", "01.0.0.0/8", "10.0.0.0/08", "10.0.0.0/-1",
     "a.b.c.d/8", " 10.0.0.0/8", "10.0.0.0/8 ", "10.0.0.0.0/8", "10.0.0.0/"],
)
def test_invalid(bad):
    with pytest.raises(ValueError):
        merge_cidrs(["10.0.0.0/8", bad])


def test_random_against_ipaddress():
    # The standard library's collapse_addresses is an independent oracle.
    rng = random.Random(81)
    for _ in range(150):
        blocks = []
        for _ in range(rng.randint(1, 8)):
            prefix = rng.randint(22, 32)
            addr = (10 << 24) | rng.randint(0, 2**12 - 1)
            blocks.append(f"{ipaddress.IPv4Address(addr)}/{prefix}")
        nets = [ipaddress.ip_network(b, strict=False) for b in blocks]
        expected = [str(n) for n in sorted(ipaddress.collapse_addresses(nets))]
        assert list(merge_cidrs(blocks)) == expected, blocks
