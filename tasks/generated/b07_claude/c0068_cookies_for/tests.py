import pytest
from solution import cookies_for

S = ["a=1; Path=/docs", "b=2", "c=3; Path=/docs/api", "d=4; path=/doc"]


@pytest.mark.parametrize(
    "set_cookies, path, expected",
    [
        (S, "/docs/api/v1", "c=3; a=1; b=2"),
        (S, "/docsx", "b=2"),
        (S, "/docs", "a=1; b=2"),
        (S, "/doc", "d=4; b=2"),
        (S, "/doc/x", "d=4; b=2"),
        (S, "/", "b=2"),
        ([], "/", ""),
        (["x=1", "y=2", "x=3"], "/", "x=3; y=2"),
        (["x=1", "x=; Max-Age=0"], "/", ""),
        (["x=1", "x=2; Max-Age=-1"], "/", ""),
        (["x=1", "x=2; Max-Age=60"], "/", "x=2"),
        (["x=1", "x=2; Max-Age=1"], "/", "x=2"),
        (["x=1", "x=2; Max-Age=soon"], "/", "x=2"),
        (["x=1; Path=/a", "x=2; Max-Age=0"], "/a", "x=1"),
        (["x=1; Max-Age=0"], "/", ""),
        (["x=1; Max-Age=0", "x=2"], "/", "x=2"),
        (["x=1", "y=2", "x=; Max-Age=0", "x=3"], "/", "y=2; x=3"),
        (["x=1; Path=relative"], "/any/where", "x=1"),
        (["x=1; Path="], "/q", "x=1"),
        (["x=1; Path=/docs/"], "/docs", ""),
        (["x=1; Path=/docs/"], "/docs/", "x=1"),
        (["x=1; Path=/docs/"], "/docs/a", "x=1"),
        (["novalue", "=x", " = y", "ok=1"], "/", "ok=1"),
        (["a=b=c"], "/", "a=b=c"),
        (["  a = 1 ;  Path = /p  "], "/p", "a=1"),
        (["s=root", "s=deep; Path=/x"], "/x/y", "s=deep; s=root"),
        (["a=1; Path=/x; Path=/y"], "/y", "a=1"),
        (["a=1; Path=/x; Path=/y"], "/x", ""),
        (["a=1; PATH=/x; Secure; HttpOnly"], "/x/1", "a=1"),
        (['q="quoted value"'], "/", 'q="quoted value"'),
        (["e="], "/", "e="),
        (["z=1", "y=1; Path=/a", "x=1; Path=/a/b"], "/a/b/c", "x=1; y=1; z=1"),
        (["n=1; max-age=0 ; Path=/"], "/", ""),
    ],
)
def test_examples(set_cookies, path, expected):
    assert cookies_for(set_cookies, path) == expected


@pytest.mark.parametrize("path", ["", "docs", " /docs"])
def test_invalid_path(path):
    with pytest.raises(ValueError):
        cookies_for(["a=1"], path)
