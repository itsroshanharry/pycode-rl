import pytest
from solution import freshness

D = "Sun, 06 Nov 1994 08:49:37 GMT"
D_PLUS_HOUR = "Sun, 06 Nov 1994 09:49:37 GMT"


@pytest.mark.parametrize(
    "headers, shared, expected",
    [
        ({"Cache-Control": "public, max-age=600, s-maxage=60"}, True, 60),
        ({"Cache-Control": "public, max-age=600, s-maxage=60"}, False, 600),
        ({"date": D, "EXPIRES": D_PLUS_HOUR}, False, 3600),
        ({}, False, None),
        ({"Cache-Control": ""}, True, None),
        ({"Cache-Control": "public"}, True, None),
        ({"Cache-Control": "max-age=0"}, False, 0),
        ({"Cache-Control": "MAX-AGE=30"}, False, 30),
        ({"cache-control": "Max-Age=30"}, False, 30),
        ({"Cache-Control": 'max-age="45"'}, False, 45),
        ({"Cache-Control": "max-age=007"}, False, 7),
        ({"Cache-Control": "max-age=abc"}, False, 0),
        ({"Cache-Control": "max-age=-1"}, False, 0),
        ({"Cache-Control": "max-age=1.5"}, False, 0),
        ({"Cache-Control": "max-age"}, False, 0),
        ({"Cache-Control": 'max-age=""'}, False, 0),
        ({"Cache-Control": "max-age=60, max-age=60"}, False, 0),
        ({"Cache-Control": "max-age=60, MAX-AGE=70"}, False, 0),
        ({"Cache-Control": "max-age=99999999999"}, False, 2147483648),
        ({"Cache-Control": "max-age=2147483648"}, False, 2147483648),
        ({"Cache-Control": "max-age=2147483647"}, False, 2147483647),
        ({"Cache-Control": "no-cache, max-age=600"}, False, 0),
        ({"Cache-Control": "max-age=600, NO-CACHE"}, True, 0),
        ({"Cache-Control": 'no-cache="Set-Cookie", max-age=600'}, False, 600),
        ({"Cache-Control": 'no-cache="Set-Cookie, Set-Cookie2", max-age=600'}, False, 600),
        ({"Cache-Control": 'private="x,max-age=5", max-age=600'}, False, 600),
        ({"Cache-Control": "no-cache=foo"}, False, None),
        ({"Cache-Control": "s-maxage=60"}, False, None),
        ({"Cache-Control": "s-maxage=60, s-maxage=60, max-age=600"}, True, 0),
        ({"Cache-Control": "s-maxage=bad, max-age=600"}, True, 0),
        ({"Cache-Control": "s-maxage=bad, max-age=600"}, False, 600),
        ({"Cache-Control": " , ,max-age=5 ,\t, "}, False, 5),
        ({"Cache-Control": "max-age=5", "Expires": "garbage"}, False, 5),
        ({"Expires": "garbage", "Date": D}, False, 0),
        ({"Expires": "0"}, False, 0),
        ({"Expires": D_PLUS_HOUR}, False, None),
        ({"Expires": D_PLUS_HOUR, "Date": "garbage"}, False, None),
        ({"Expires": D, "Date": D_PLUS_HOUR}, False, 0),
        ({"Expires": D, "Date": D}, False, 0),
        ({"Expires": "Mon, 06 Nov 1994 09:49:37 GMT", "Date": D}, False, 0),
        ({"Expires": "Sun, 06 nov 1994 09:49:37 GMT", "Date": D}, False, 0),
        ({"Expires": "Sun, 06 Nov 1994 09:49:37 UTC", "Date": D}, False, 0),
        ({"Expires": "Sun, 6 Nov 1994 09:49:37 GMT", "Date": D}, False, 0),
        ({"Expires": "Sun, 06 Nov 1994 09:49:60 GMT", "Date": D}, False, 0),
        ({"Expires": "Thu, 29 Feb 2024 00:00:00 GMT", "Date": "Wed, 28 Feb 2024 00:00:00 GMT"}, False, 86400),
        ({"Expires": "Sun, 29 Feb 2023 00:00:00 GMT", "Date": "Tue, 28 Feb 2023 00:00:00 GMT"}, False, 0),
        ({"Expires": "Fri, 01 Jan 2100 00:00:00 GMT", "Date": "Thu, 31 Dec 2099 23:59:59 GMT"}, False, 1),
        ({"Expires": D_PLUS_HOUR, "Date": D, "Cache-Control": "public"}, True, 3600),
        ({"Expires": D_PLUS_HOUR, "Date": D, "Cache-Control": "s-maxage=10"}, False, 3600),
        ({"Cache-Control": "max-age=10", "X-Other": "no-cache"}, False, 10),
    ],
)
def test_examples(headers, shared, expected):
    assert freshness(headers, shared) == expected


@pytest.mark.parametrize(
    "headers",
    [
        {"Cache-Control": "max-age=60", "cache-control": "max-age=60"},
        {"Date": D, "DATE": D},
        {"Cache-Control": "max-age="},
        {"Cache-Control": "max-age = 60"},
        {"Cache-Control": "max-age 60"},
        {"Cache-Control": "=60"},
        {"Cache-Control": 'no-cache="unterminated'},
        {"Cache-Control": 'no-cache="a\\"b"'},
        {"Cache-Control": "max-age=60;"},
        {"Cache-Control": "max-age=60 public"},
        {"Cache-Control": "no cache"},
        {"Cache-Control": "max-age=(60)"},
    ],
)
def test_malformed(headers):
    with pytest.raises(ValueError):
        freshness(headers, True)
