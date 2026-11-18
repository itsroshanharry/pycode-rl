import random

import pytest
from solution import render_template


@pytest.mark.parametrize(
    "template, variables, expected",
    [
        ("Hi ${user}, you owe $$${amount:-0}.", {"user": "Ann"}, "Hi Ann, you owe $0."),
        ("${a}${b:-x}", {"a": "${b}", "b": ""}, "${b}x"),
        ("", {}, ""),
        ("no variables here", {}, "no variables here"),
        ("$$", {}, "$"),
        ("$$$$", {}, "$$"),
        ("${x}", {"x": ""}, ""),
        ("${x:-d}", {"x": ""}, "d"),
        ("${x:-d}", {}, "d"),
        ("${x:-d}", {"x": "v"}, "v"),
        ("${x:-}", {}, ""),
        ("${_a1}", {"_a1": "ok"}, "ok"),
        ("${x}${x}", {"x": "ab"}, "abab"),
        ("a${x:-b c}d", {}, "ab cd"),
        ("${x:-$}", {}, "$"),
        ("${x:-${y}", {}, "${y"),
        ("pi=${p}", {"p": "3.14", "q": "unused"}, "pi=3.14"),
        ("{not a var} ${a}", {"a": "1"}, "{not a var} 1"),
        ("$${a}", {"a": "1"}, "${a}"),
    ],
)
def test_render(template, variables, expected):
    assert render_template(template, variables) == expected


@pytest.mark.parametrize("template, variables", [("${missing}", {}), ("${a}", {"b": "1"}), ("x ${A}", {"a": "1"})])
def test_missing_variable(template, variables):
    with pytest.raises(KeyError):
        render_template(template, variables)


@pytest.mark.parametrize("template", ["$", "a$", "$a", "${}", "${1a}", "${a", "${a-b}", "${a:b}", "$ {a}", "${ a}", "${a b}"])
def test_malformed(template):
    with pytest.raises(ValueError):
        render_template(template, {"a": "1"})


def test_random_compositions():
    # Build templates from pieces whose rendering is known, then compare.
    rng = random.Random(26)
    variables = {"a": "1", "b": "", "long_name": "${a}", "z9": "$$"}
    pieces = [
        ("text ", "text "), ("$$", "$"), ("${a}", "1"), ("${b}", ""), ("${long_name}", "${a}"),
        ("${z9}", "$$"), ("${b:-dflt}", "dflt"), ("${a:-dflt}", "1"), ("${nope:-}", ""), ("{x}", "{x}"),
    ]
    for _ in range(200):
        chosen = [rng.choice(pieces) for _ in range(rng.randint(0, 8))]
        template = "".join(p for p, _ in chosen)
        assert render_template(template, variables) == "".join(e for _, e in chosen), template
