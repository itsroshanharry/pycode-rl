from __future__ import annotations  # every annotation below is a string

import enum
import functools
import typing
from dataclasses import dataclass, field

# Regression (leaderboard 2026-11-20): valid code that looks itself up in sys.modules
# (dataclasses with string annotations, typing.get_type_hints, singledispatch with
# annotations) failed to load when the worker ran the candidate in a bare namespace.


class Sign(enum.Enum):
    NEG = -1
    POS = 1


@dataclass(frozen=True)
class Digits:
    sign: Sign
    values: list[int] = field(default_factory=list)


@functools.singledispatch
def _check(n: object) -> None:
    raise TypeError("not an int")


@_check.register
def _(n: int) -> None:
    if isinstance(n, bool):
        raise TypeError("bool is not an int")


def digit_sum(n: int) -> int:
    if type(n) is not int:
        raise TypeError("not an int")
    _check(n)
    assert typing.get_type_hints(Digits)["values"] == list[int]
    d = Digits(Sign.NEG if n < 0 else Sign.POS, [int(c) for c in str(abs(n))])
    return sum(d.values)
