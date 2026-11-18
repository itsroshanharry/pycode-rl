import re

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def render_template(template: str, variables: dict[str, str]) -> str:
    out: list[str] = []
    i, n = 0, len(template)
    while i < n:
        c = template[i]
        if c != "$":
            out.append(c)
            i += 1
            continue
        nxt = template[i + 1 : i + 2]
        if nxt == "$":
            out.append("$")
            i += 2
            continue
        if nxt != "{":
            raise ValueError(f"stray '$' at position {i}")
        end = template.find("}", i + 2)
        if end == -1:
            raise ValueError("unclosed '${'")
        name, sep, default = template[i + 2 : end].partition(":-")
        if not _NAME.fullmatch(name):
            raise ValueError(f"invalid variable name {name!r}")
        if sep:
            value = variables.get(name)
            out.append(value if value else default)
        else:
            if name not in variables:
                raise KeyError(name)
            out.append(variables[name])
        i = end + 1
    return "".join(out)
