import random

import pytest
from solution import unpack_bits


@pytest.mark.parametrize(
    "value, layout, expected",
    [
        (0b11010110, [("mode", 0, 3), ("delta!", 3, 4), ("flag", 7, 1)], [("mode", 6), ("delta", -6), ("flag", 1)]),
        (0, [], []),
        (0, [("a", 0, 1)], [("a", 0)]),
        (0xAB, [("hi", 4, 4), ("lo", 0, 4)], [("lo", 0xB), ("hi", 0xA)]),
        (0b1000, [("s!", 0, 4)], [("s", -8)]),
        (0b0111, [("s!", 0, 4)], [("s", 7)]),
        (0b1111, [("s!", 0, 4)], [("s", -1)]),
        (1, [("b!", 0, 1)], [("b", -1)]),
        (0, [("b!", 0, 1)], [("b", 0)]),
        (0b1010_0000, [("x", 5, 3)], [("x", 0b101)]),
        (0, [("x", 5, 3), ("y", 0, 5)], [("y", 0), ("x", 0)]),
        ((1 << 100) | 5, [("big", 100, 1), ("low", 0, 3)], [("low", 5), ("big", 1)]),
        ((0x8000 << 16) | 0xFFFF, [("a!", 16, 16), ("b!", 0, 16)], [("b", -1), ("a", -32768)]),
        (0b11, [("a", 0, 1), ("b", 1, 1)], [("a", 1), ("b", 1)]),
        (0b101, [("z", 2, 1), ("m", 1, 1), ("a", 0, 1)], [("a", 1), ("m", 0), ("z", 1)]),
    ],
)
def test_examples(value, layout, expected):
    assert list(unpack_bits(value, layout).items()) == expected


@pytest.mark.parametrize(
    "value, layout",
    [
        (-1, [("a", 0, 8)]),
        (0, [("a", -1, 2)]),
        (0, [("a", 0, 0)]),
        (0, [("a", 0, 4), ("b", 3, 2)]),
        (0, [("b", 3, 2), ("a", 0, 4)]),
        (0, [("a", 2, 3), ("b", 2, 1)]),
        (0, [("a", 0, 2), ("a", 2, 2)]),
        (0, [("a", 0, 2), ("a!", 2, 2)]),
        (0, [("a!", 0, 2), ("a", 2, 2)]),
        (0, [("!", 0, 2)]),
        (0, [("", 0, 2)]),
        (0b100, [("a", 0, 2)]),
        (0b100, [("a", 0, 2), ("b", 3, 2)]),
        (1, []),
        (1 << 64, [("a", 0, 64)]),
    ],
)
def test_invalid(value, layout):
    with pytest.raises(ValueError):
        unpack_bits(value, layout)


def test_random_round_trip():
    rng = random.Random(86)
    for _ in range(300):
        pos, layout, want = 0, [], {}
        for i in range(rng.randint(1, 8)):
            pos += rng.choice([0, 0, 1, 3])  # unused gaps between fields
            width = rng.randint(1, 12)
            signed = rng.random() < 0.4
            v = rng.randint(-(1 << (width - 1)), (1 << (width - 1)) - 1) if signed else rng.randint(0, (1 << width) - 1)
            layout.append((f"f{i}" + ("!" if signed else ""), pos, width))
            want[f"f{i}"] = (pos, width, v)
            pos += width
        value = sum((v & ((1 << w) - 1)) << p for p, w, v in want.values())
        rng.shuffle(layout)
        got = unpack_bits(value, layout)
        assert list(got.items()) == [(k, v) for k, (_, _, v) in sorted(want.items(), key=lambda kv: kv[1][0])]
