import itertools
import random

import pytest
from solution import packbits

APPLE_IN = bytes.fromhex("AAAAAA80002AAAAAAAAA80002A22AAAAAAAAAAAAAAAAAAAA")
APPLE_OUT = bytes.fromhex("FEAA0280002AFDAA0380002A22F7AA")  # Apple Technical Note TN1023


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"", b""),
        (b"A", b"\x00A"),
        (b"AB", b"\x01AB"),
        (b"AA", b"\x01AA"),
        (b"AAA", b"\xfeA"),
        (b"AAAB", b"\xfeA\x00B"),
        (b"ABBBC", b"\x00A\xfeB\x00C"),
        (b"AABBB", b"\x01AA\xfeB"),
        (bytes([1, 2, 2, 3, 3, 3]), b"\x02\x01\x02\x02\xfe\x03"),
        (APPLE_IN, APPLE_OUT),
        (bytes(128), b"\x81\x00"),
        (bytes(129), b"\x81\x00\x00\x00"),
        (bytes(130), b"\x81\x00\x01\x00\x00"),
        (bytes(131), b"\x81\x00\xfe\x00"),
        (bytes(256), b"\x81\x00\x81\x00"),
        (bytes(range(128)), b"\x7f" + bytes(range(128))),
        (bytes(range(129)), b"\x7f" + bytes(range(128)) + b"\x00\x80"),
        (bytes(range(127)) + b"\x05\x05\x05", b"\x7e" + bytes(range(127)) + b"\xfe\x05"),
        (b"\xff\xff\xff\xff", b"\xfd\xff"),
    ],
)
def test_examples(data, expected):
    assert packbits(data) == expected


def test_returns_bytes():
    assert type(packbits(b"abc")) is bytes


def _unpack(enc):
    out, i = bytearray(), 0
    while i < len(enc):
        h = enc[i]
        if h < 128:
            out += enc[i + 1: i + 2 + h]
            i += 2 + h
        else:
            assert h != 128
            out += bytes([enc[i + 1]]) * (257 - h)
            i += 2
    return bytes(out)


def _oracle(data):
    out, lit = bytearray(), bytearray()

    def flush():
        if lit:
            out.append(len(lit) - 1)
            out.extend(lit)
            lit.clear()

    for b, grp in itertools.groupby(data):
        n = len(list(grp))
        while n:
            c = min(n, 128)
            if c >= 3:
                flush()
                out += bytes([257 - c, b])
            else:
                for _ in range(c):
                    lit.append(b)
                    if len(lit) == 128:
                        flush()
            n -= c
    flush()
    return bytes(out)


def test_random_against_oracle():
    rng = random.Random(87)
    for _ in range(300):
        parts = []
        for _ in range(rng.randint(0, 12)):
            parts.append(bytes([rng.choice([0, 1, 7, 255])]) * rng.choice([1, 1, 2, 3, 4, 127, 128, 129, 200]))
            if rng.random() < 0.3:
                parts.append(bytes(rng.randrange(256) for _ in range(rng.randint(1, 150))))
        data = b"".join(parts)
        enc = packbits(data)
        assert enc == _oracle(data)
        assert _unpack(enc) == data
