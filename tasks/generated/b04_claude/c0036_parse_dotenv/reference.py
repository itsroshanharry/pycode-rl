import re

_LINE = re.compile(r"\s*(?:export +)?([A-Za-z_][A-Za-z0-9_]*) *= *(.*)", re.DOTALL)
_AFTER_QUOTE = re.compile(r"\s*(?:#.*)?", re.DOTALL)
_ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


def _quoted(rest: str, quote: str) -> tuple[str, str]:
    out, i = [], 1
    while i < len(rest):
        c = rest[i]
        if c == quote:
            return "".join(out), rest[i + 1 :]
        if c == "\\" and quote == '"':
            nxt = rest[i + 1 : i + 2]
            if nxt not in _ESCAPES:
                raise ValueError(f"bad escape \\{nxt}")
            out.append(_ESCAPES[nxt])
            i += 2
            continue
        out.append(c)
        i += 1
    raise ValueError("unterminated quoted value")


def parse_dotenv(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _LINE.fullmatch(line)
        if not m:
            raise ValueError(f"malformed line: {line!r}")
        name, rest = m.groups()
        if rest[:1] in ("'", '"'):
            value, tail = _quoted(rest, rest[0])
            if not _AFTER_QUOTE.fullmatch(tail):
                raise ValueError(f"text after closing quote: {line!r}")
        else:
            cut = rest.find(" #")
            value = (rest if cut == -1 else rest[:cut]).rstrip()
        env[name] = value
    return env
