import random

import pytest
from solution import log_counts


def _norm(result):
    rows, bad = result
    return [tuple(r) for r in rows], bad


@pytest.mark.parametrize(
    "lines, expected",
    [
        (["2024-05-01T10:15:42Z [error] disk full", "2024-05-01T10:15:59.123 WARNING slow", "oops"],
         ([("2024-05-01T10:15", "WARN", 1), ("2024-05-01T10:15", "ERROR", 1)], 1)),
        ([], ([], 0)),
        (["", "   ", "\n", "\t\r\n"], ([], 0)),
        (["2024-01-01T00:00:00 INFO a", "2024-01-01T00:00:59 info b", "2024-01-01T00:01:00 Info"],
         ([("2024-01-01T00:00", "INFO", 2), ("2024-01-01T00:01", "INFO", 1)], 0)),
        (["2024-01-01T00:00:00 ERROR x", "2024-01-01T00:00:00 DEBUG x", "2024-01-01T00:00:00 INFO x", "2024-01-01T00:00:00 WARN x"],
         ([("2024-01-01T00:00", "DEBUG", 1), ("2024-01-01T00:00", "INFO", 1), ("2024-01-01T00:00", "WARN", 1), ("2024-01-01T00:00", "ERROR", 1)], 0)),
        (["2024-01-01T00:00:00 [WARN] a", "2024-01-01T00:00:00 [Warning] b"], ([("2024-01-01T00:00", "WARN", 2)], 0)),
        (["2024-01-01T00:00:00     ERROR many spaces"], ([("2024-01-01T00:00", "ERROR", 1)], 0)),
        (["2024-01-01T00:00:00 ERROR"], ([("2024-01-01T00:00", "ERROR", 1)], 0)),
        (["2024-01-01T00:00:00 ERROR "], ([("2024-01-01T00:00", "ERROR", 1)], 0)),
        (["2024-01-01T00:00:00 ERROR\n", "2024-01-01T00:00:00 ERROR x\r\n"], ([("2024-01-01T00:00", "ERROR", 2)], 0)),
        (["2024-01-01T00:00:00.5Z ERROR [nested] brackets ok"], ([("2024-01-01T00:00", "ERROR", 1)], 0)),
        (["2024-01-02T00:00:00 INFO", "2023-12-31T23:59:59 INFO"],
         ([("2023-12-31T23:59", "INFO", 1), ("2024-01-02T00:00", "INFO", 1)], 0)),
        ([" 2024-01-01T00:00:00 INFO x"], ([], 1)),
        (["2024-01-01T00:00:00 [ERROR x"], ([], 1)),
        (["2024-01-01T00:00:00 ERROR] x"], ([], 1)),
        (["2024-01-01T00:00:00 FATAL x"], ([], 1)),
        (["2024-01-01T00:00:00 ERRORx"], ([], 1)),
        (["2024-01-01T00:00:00ERROR x"], ([], 1)),
        (["2024-01-01T00:00:60 ERROR x"], ([], 1)),
        (["2023-02-29T00:00:00 ERROR x"], ([], 1)),
        (["2024-01-01 00:00:00 ERROR x"], ([], 1)),
        (["2024-01-01T00:00 ERROR x"], ([], 1)),
        (["2024-01-01T00:00:00. ERROR x"], ([], 1)),
        (["2024-01-01T00:00:00ZZ ERROR x"], ([], 1)),
        (["2024-01-01T00:00:00 ERROR\tx"], ([], 1)),
        (["2024-01-01T00:00:00 [ ERROR ] x"], ([], 1)),
        (["２024-01-01T00:00:00 ERROR x"], ([], 1)),
        (["2024-01-01T00:00:00 İNFO x"], ([], 1)),
    ],
)
def test_examples(lines, expected):
    assert _norm(log_counts(lines)) == expected


def test_random_against_oracle():
    rng = random.Random(27)
    order = ["DEBUG", "INFO", "WARN", "ERROR"]
    for _ in range(200):
        lines, want, bad = [], {}, 0
        for _ in range(rng.randint(0, 30)):
            minute = f"2024-03-0{rng.randint(1, 3)}T1{rng.randint(0, 2)}:0{rng.randint(0, 2)}"
            lvl = rng.choice(["debug", "INFO", "Warn", "WARNING", "error", "TRACE"])
            sec = rng.choice(["00", "30", "59", "60"])
            ts = f"{minute}:{sec}" + rng.choice(["", "Z", ".25", ".25Z"])
            word = f"[{lvl}]" if rng.random() < 0.5 else lvl
            lines.append(f"{ts}{' ' * rng.randint(1, 3)}{word}" + rng.choice(["", " msg", " a b c"]))
            norm = {"WARNING": "WARN"}.get(lvl.upper(), lvl.upper())
            if sec == "60" or norm not in order:
                bad += 1
            else:
                want[(minute, norm)] = want.get((minute, norm), 0) + 1
        rows = sorted(((m, l, n) for (m, l), n in want.items()), key=lambda r: (r[0], order.index(r[1])))
        assert _norm(log_counts(lines)) == (rows, bad), lines
