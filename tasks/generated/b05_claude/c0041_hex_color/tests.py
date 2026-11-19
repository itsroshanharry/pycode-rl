import random

import pytest
from solution import hex_color


@pytest.mark.parametrize(
    "text, expected",
    [
        ("#F0A", "#ff00aaff"),
        ("#11223380", "#11223380"),
        ("#000", "#000000ff"),
        ("#fff", "#ffffffff"),
        ("#0000", "#00000000"),
        ("#abcd", "#aabbccdd"),
        ("#AbCd", "#aabbccdd"),
        ("#123456", "#123456ff"),
        ("#ABCDEF", "#abcdefff"),
        ("#a1B2c3D4", "#a1b2c3d4"),
        ("#ffffff00", "#ffffff00"),
        ("#9", None),
    ],
)
def test_examples(text, expected):
    if expected is None:
        with pytest.raises(ValueError):
            hex_color(text)
    else:
        assert hex_color(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "", "#", "fff", "ffffff", "#ff", "#fffff", "#fffffff", "#fffffffff", "##fff", "#ggg",
        "#f_f", "#f_f0f0", "#+ff", "#-fff", "# fff", "#fff ", " #fff", "0xfff", "#0xfff",
        "#１２３", "#١٢٣", "#fff\n", "#FfFfFfFfF", "rgb(0,0,0)",
    ],
)
def test_invalid(text):
    with pytest.raises(ValueError):
        hex_color(text)


def test_random_round_trip():
    rng = random.Random(98)
    hexd = "0123456789abcdefABCDEF"
    for _ in range(300):
        n = rng.choice([3, 4, 6, 8])
        digits = "".join(rng.choice(hexd) for _ in range(n))
        low = digits.lower()
        if n in (3, 4):
            low = "".join(c + c for c in low)
        want = "#" + low + ("ff" if len(low) == 6 else "")
        assert hex_color("#" + digits) == want
