import re

_INLINE = re.compile(r"\s[;#]")


def parse_ini(text: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {"": {}}
    section = ""
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or line[0] in ";#":
            continue
        if line.startswith("[") and line.endswith("]"):
            name = line[1:-1].strip()
            if not name or "[" in name or "]" in name:
                raise ValueError(f"bad section header: {raw!r}")
            section = name
            result.setdefault(section, {})
            continue
        key, sep, value = line.partition("=")
        key = key.strip().lower()
        if not sep or not key:
            raise ValueError(f"bad line: {raw!r}")
        m = _INLINE.search(value)
        if m:
            value = value[: m.start()]
        result[section][key] = value.strip()
    if not result[""]:
        del result[""]
    return result
