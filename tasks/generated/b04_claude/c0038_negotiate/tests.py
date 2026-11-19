import random

import pytest
from solution import negotiate


@pytest.mark.parametrize(
    "accept, offered, expected",
    [
        ("text/html;q=0.8, application/json", ["text/html", "application/json"], "application/json"),
        ("text/*;q=0.5, text/plain;q=0", ["text/plain", "text/csv"], "text/csv"),
        ("", ["a/b", "c/d"], "a/b"),
        ("   ", ["x/y"], "x/y"),
        (" , ,\t", ["x/y"], "x/y"),
        ("a/b,,c/d;q=0.5,", ["c/d", "a/b"], "a/b"),
        ("text/html", ["application/json"], None),
        ("*/*;q=0", ["a/b"], None),
        ("text/html", [], None),
        ("*/*;q=0.1, text/*;q=0.2, text/html;q=0.3", ["image/png", "text/plain", "text/html"], "text/html"),
        ("*/*;q=0.1, text/*;q=0.2, text/html;q=0.3", ["image/png", "text/plain"], "text/plain"),
        ("*/*;q=0.1, text/*;q=0.2", ["image/png"], "image/png"),
        ("text/*, text/html;q=0.1", ["text/html", "text/plain"], "text/plain"),
        ("*/*, text/*;q=0", ["text/html", "image/png"], "image/png"),
        ("*/*;q=0.9, a/b;q=0.2", ["a/b", "c/d"], "c/d"),
        ("TEXT/HTML", ["text/html"], "text/html"),
        ("text/html", ["Text/HTML"], "Text/HTML"),
        ("Text/*;q=0.5", ["TEXT/csv", "x/y"], "TEXT/csv"),
        ("a/b;q=0.5, c/d;q=0.5", ["c/d", "a/b"], "c/d"),
        ("a/b;q=0.5, c/d;q=0.5", ["a/b", "c/d"], "a/b"),
        ("a/b, c/d", ["c/d", "a/b", "c/d"], "c/d"),
        ("a/b;q=0.3, a/b;q=0.7, c/d;q=0.5", ["c/d", "a/b"], "a/b"),
        ("a/b;q=0.7, a/b;q=0.3, c/d;q=0.5", ["c/d", "a/b"], "a/b"),
        ("text/html;level=1;q=0.5, application/xml;q=0.4", ["application/xml", "text/html"], "text/html"),
        ("text/html;Q=0.2, a/b;q=0.3", ["text/html", "a/b"], "a/b"),
        ("a/b;q=1.000, c/d;q=0.999", ["c/d", "a/b"], "a/b"),
        ("a/b;q=0., c/d;q=0.001", ["a/b", "c/d"], "c/d"),
        ("a/b;q=1., c/d", ["c/d", "a/b"], "c/d"),
        ("a/b;q=0.5, c/d;q=0.50", ["c/d", "a/b"], "c/d"),
        ("a/b;q=0.333, c/d;q=0.334", ["a/b", "c/d"], "c/d"),
        ("\ta/b\t;\tq=0.5\t, c/d;q=0.4", ["c/d", "a/b"], "a/b"),
        ("application/vnd.api+json;q=0.9, */*;q=0.1", ["text/html", "application/vnd.api+json"], "application/vnd.api+json"),
        ("a/b;charset=utf-8", ["a/b"], "a/b"),
    ],
)
def test_examples(accept, offered, expected):
    assert negotiate(accept, offered) == expected


@pytest.mark.parametrize(
    "accept",
    [
        "text", "text/", "/html", "*/html", "te xt/html", "text/html/x", "text/html;",
        "text/html;q=2", "text/html;q=1.001", "text/html;q=0.1234", "text/html;q=.5",
        "text/html;q=", "text/html;q=-0", "text/html;q=1.0000", "text/html;q=0x1",
        "text/html; q = 0.5", "text/html;q =0.5", "text/html;q=0.5;q=0.6", "text/html;q=0.5;Q=0.5",
        "text/html;level", "text/html;=1", "a/b, c", "a/b;q=0.5, c/d;q=high", "text/h(tml",
    ],
)
def test_invalid(accept):
    with pytest.raises(ValueError):
        negotiate(accept, ["text/html"])


_RANGES = ["a/b", "a/c", "a/*", "b/b", "b/*", "*/*", "A/B", "a/B", "B/*"]
_OFFERED = ["a/b", "a/c", "b/b", "b/c", "c/c", "A/b"]
_QS = [0, 1, 10, 100, 250, 500, 999, 1000]


def _fmt_q(q, rng):
    if q == 1000:
        return rng.choice(["1", "1.", "1.0", "1.000"])
    digits = f"{q:03d}"
    short = digits.rstrip("0")
    return rng.choice(["0." + short if short else "0", "0." + digits])


def _oracle(ranges, offered):
    ranges = ranges or [("*", "*", 1000)]
    best, best_q = None, 0
    for o in offered:
        t, s = o.lower().split("/")
        q = 0
        for level in (lambda r: r[0] == t and r[1] == s, lambda r: r[0] == t and r[1] == "*", lambda r: r[0] == "*"):
            qs = [r[2] for r in ranges if level(r)]
            if qs:
                q = max(qs)
                break
        if q > best_q:
            best, best_q = o, q
    return best


def test_random_against_oracle():
    rng = random.Random(22)
    for _ in range(400):
        parts, ranges = [], []
        for _ in range(rng.randint(0, 5)):
            media = rng.choice(_RANGES)
            if rng.random() < 0.3:
                q, text = 1000, media
            else:
                q = rng.choice(_QS)
                text = f"{media}{rng.choice(['', ' '])};{rng.choice(['q', 'Q'])}={_fmt_q(q, rng)}"
            if rng.random() < 0.2:
                text += ";x=1"
            parts.append(text)
            t, s = media.lower().split("/")
            ranges.append((t, s, q))
        accept = rng.choice([",", ", ", " ,"]).join(parts)
        offered = rng.sample(_OFFERED, rng.randint(0, 4))
        assert negotiate(accept, offered) == _oracle(ranges, offered), (accept, offered)
