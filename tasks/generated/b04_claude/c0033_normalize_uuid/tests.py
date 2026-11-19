import random
import uuid

import pytest
from solution import normalize_uuid

CANON = "123e4567-e89b-12d3-a456-426614174000"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("{123E4567-E89B-12D3-A456-426614174000}", CANON),
        ("123e4567e89b12d3a456426614174000", CANON),
        (CANON, CANON),
        (CANON.upper(), CANON),
        ("urn:uuid:" + CANON, CANON),
        ("URN:UUID:" + CANON.upper(), CANON),
        ("Urn:Uuid:" + CANON, CANON),
        ("00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000"),
        ("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", "ffffffff-ffff-ffff-ffff-ffffffffffff"),
    ],
)
def test_accepted(text, expected):
    assert normalize_uuid(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "", " " + CANON, CANON + "\n", "123e4567-e89b12d3-a456-426614174000", "123e4567e89b-12d3-a456-426614174000",
        "1-23e4567e89b12d3a456426614174000", "{123e4567e89b12d3a456426614174000}", "{urn:uuid:" + CANON + "}",
        "{" + CANON, CANON + "}", "123e4567-e89b-12d3-a456-42661417400", "123e4567-e89b-12d3-a456-4266141740000",
        "g23e4567-e89b-12d3-a456-426614174000", "uuid:" + CANON, "urn:" + CANON, "urn:uuid:" + CANON.replace("-", ""),
        "123e4567-e89b-12d3-a456_426614174000",
    ],
)
def test_rejected(text):
    with pytest.raises(ValueError):
        normalize_uuid(text)


def test_random_forms():
    rng = random.Random(15)
    for _ in range(200):
        u = uuid.UUID(int=rng.getrandbits(128))
        canon = str(u)
        mixed = "".join(c.upper() if rng.random() < 0.5 else c for c in canon)
        form = rng.choice([mixed, "{" + mixed + "}", "urn:uuid:" + mixed, mixed.replace("-", "")])
        assert normalize_uuid(form) == canon, form
