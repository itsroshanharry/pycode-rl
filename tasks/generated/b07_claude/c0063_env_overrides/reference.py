import copy
import re


def env_overrides(config: dict, env: dict[str, str], prefix: str) -> dict:
    out = copy.deepcopy(config)
    head = prefix + "__"
    for name in sorted(env):
        if not name.startswith(head):
            continue
        parts = name[len(head):].split("__")
        if any(p == "" for p in parts):
            raise ValueError(f"empty key part in {name!r}")
        keys = [p.lower() for p in parts]
        node = out
        for k in keys[:-1]:
            if k not in node:
                node[k] = {}
            elif not isinstance(node[k], dict):
                raise ValueError(f"{k!r} is not a section ({name!r})")
            node = node[k]
        last, raw = keys[-1], env[name]
        current = node.get(last)
        if isinstance(current, dict):
            raise ValueError(f"cannot override section {last!r}")
        if isinstance(current, bool):  # check bool BEFORE int: bool is a subclass of int
            low = raw.lower()
            if low in ("true", "1"):
                value = True
            elif low in ("false", "0"):
                value = False
            else:
                raise ValueError(f"not a bool: {raw!r}")
        elif isinstance(current, int):
            if not re.fullmatch(r"-?[0-9]+", raw):
                raise ValueError(f"not an int: {raw!r}")
            value = int(raw)
        else:
            value = raw
        node[last] = value
    return out
