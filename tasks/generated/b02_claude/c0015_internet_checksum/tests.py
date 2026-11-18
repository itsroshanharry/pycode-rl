import random

import pytest
from solution import internet_checksum


@pytest.mark.parametrize(
    "data, expected",
    [
        (bytes([0x00, 0x01, 0xF2, 0x03, 0xF4, 0xF5, 0xF6, 0xF7]), 8717),
        (b"", 65535),
        (b"\x00", 65535),
        (b"\x00\x00", 65535),
        (b"\xff\xff", 0),
        (b"\x12", 0xEDFF),
        (b"\x12\x34", 0xEDCB),
        (b"\xff\xff\x00\x01", 0xFFFE),
        (b"\x80\x00\x80\x00", 0xFFFE),
        (b"\x00\x01\x00\x02\x00\x03", 0xFFF9),
    ],
)
def test_examples(data, expected):
    assert internet_checksum(data) == expected


def _oracle(data):
    # One's-complement sum via modular arithmetic: end-around carry == reduction mod 0xFFFF.
    if len(data) % 2:
        data += b"\x00"
    s = sum(int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2))
    folded = 0 if s == 0 else (s - 1) % 0xFFFF + 1
    return 0xFFFF - folded


def test_random_against_oracle():
    rng = random.Random(88)
    for _ in range(200):
        data = bytes(rng.randrange(256) for _ in range(rng.randint(0, 60)))
        assert internet_checksum(data) == _oracle(data), data.hex()


def test_large_input():
    data = bytes(range(256)) * 200 + b"\x7f"
    assert internet_checksum(data) == _oracle(data)


def test_appending_checksum_verifies():
    # Appending the checksum to even-length data makes the checksum of the whole zero.
    rng = random.Random(1)
    for _ in range(50):
        data = bytes(rng.randrange(256) for _ in range(2 * rng.randint(1, 20)))
        c = internet_checksum(data)
        assert internet_checksum(data + c.to_bytes(2, "big")) == 0
