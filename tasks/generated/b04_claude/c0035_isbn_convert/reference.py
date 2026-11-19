def _isbn10_check(nine: str) -> str:
    total = sum(int(d) * w for d, w in zip(nine, range(10, 1, -1)))
    c = (11 - total % 11) % 11
    return "X" if c == 10 else str(c)


def _isbn13_check(twelve: str) -> str:
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(twelve))
    return str((10 - total % 10) % 10)


def isbn_convert(isbn: str) -> str:
    s = isbn.replace("-", "").replace(" ", "")
    if len(s) == 10:
        body, check = s[:9], s[9].upper()
        if not (body.isascii() and body.isdigit()) or not (check == "X" or (check.isascii() and check.isdigit())):
            raise ValueError("malformed ISBN-10")
        if _isbn10_check(body) != check:
            raise ValueError("ISBN-10 check failed")
        twelve = "978" + body
        return twelve + _isbn13_check(twelve)
    if len(s) == 13:
        if not (s.isascii() and s.isdigit()):
            raise ValueError("malformed ISBN-13")
        if _isbn13_check(s[:12]) != s[12]:
            raise ValueError("ISBN-13 check failed")
        if not s.startswith("978"):
            raise ValueError("only 978 ISBN-13s have an ISBN-10 form")
        return s[3:12] + _isbn10_check(s[3:12])
    raise ValueError("an ISBN has 10 or 13 characters")
