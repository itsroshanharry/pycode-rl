import pytest
from solution import digit_sum


@pytest.mark.parametrize("n, expected", [(0, 0), (5, 5), (123, 6), (999, 27), (10**12, 1), (-45, 9), (1000001, 2)])
def test_values(n, expected):
    assert digit_sum(n) == expected


def test_rejects_non_int():
    with pytest.raises(TypeError):
        digit_sum("12")
