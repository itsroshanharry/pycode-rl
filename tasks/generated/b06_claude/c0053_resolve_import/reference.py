import keyword
import re

_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_DOTTED = rf"{_IDENT}(?:\.{_IDENT})*"
_STMT = re.compile(rf"from (\.*)({_DOTTED})? import (.+)")
_ITEM = re.compile(rf"({_IDENT})(?: +as +({_IDENT}))?")


def _check_dotted(name: str) -> None:
    if not re.fullmatch(_DOTTED, name) or any(keyword.iskeyword(p) for p in name.split(".")):
        raise ValueError(f"bad dotted name: {name!r}")


def resolve_import(importer: str, is_package: bool, statement: str) -> list[str]:
    _check_dotted(importer)
    m = _STMT.fullmatch(statement)
    if not m:
        raise ValueError(f"malformed statement: {statement!r}")
    dots, name, names = m.group(1), m.group(2) or "", m.group(3)
    if not dots and not name:
        raise ValueError("empty source module")
    if name:
        _check_dotted(name)

    paren = names.startswith("(") and names.endswith(")")
    if paren:
        names = names[1:-1]
    if names == "*" and not paren:
        items = ["*"]
    else:
        parts = [p.strip(" ") for p in names.split(",")]
        if paren and len(parts) > 1 and parts[-1] == "":
            parts.pop()  # trailing comma, allowed only inside parentheses
        items = []
        for part in parts:
            im = _ITEM.fullmatch(part)
            if not im or any(keyword.iskeyword(x) for x in im.groups() if x):
                raise ValueError(f"bad import item: {part!r}")
            items.append(im.group(1))

    level = len(dots)
    if level == 0:
        source = name
    else:
        # Same rule as importlib._bootstrap._resolve_name.
        package = importer if is_package else importer.rpartition(".")[0]
        if not package:
            raise ValueError("relative import with no parent package")
        bits = package.rsplit(".", level - 1)
        if len(bits) < level:
            raise ValueError("relative import beyond top-level package")
        source = bits[0] + ("." + name if name else "")
    return [f"{source}.{item}" for item in items]
