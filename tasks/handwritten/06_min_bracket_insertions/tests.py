import pytest
from solution import min_bracket_insertions


@pytest.mark.parametrize(
    "s, expected",
    [
        ("(]", 2),
        ("([)]", 2),
        ("", 0),
        ("()", 0),
        ("(", 1),
        (")", 1),
        ("][", 2),
        ("{[()]}", 0),
        ("(((", 3),
        (")))", 3),
        ("([]", 1),
        ("())(", 2),
        ("{(})", 2),
        ("[{]}", 2),
        ("([)", 1),
        ("(((())))", 0),
        ("()[]{}", 0),
        ("([{", 3),
        ("}])", 3),
        ("(()", 1),
        ("([{" * 10, 30),
        (")(" * 20, 2),
        ("{[(" * 6 + ")]}" * 6, 0),
        ("([{}])" * 6 + "(", 1),
    ],
)
def test_examples(s, expected):
    assert min_bracket_insertions(s) == expected
