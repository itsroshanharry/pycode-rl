import copy


def _merge(base: dict, over: dict, policy: str, path: str) -> dict:
    out = copy.deepcopy(base)
    for key, value in over.items():
        where = f"{path}.{key}" if path else key
        if value is None:
            out.pop(key, None)
            continue
        if key not in out:
            out[key] = _merge({}, value, policy, where) if isinstance(value, dict) else copy.deepcopy(value)
            continue
        cur = out[key]
        if isinstance(cur, dict) and isinstance(value, dict):
            out[key] = _merge(cur, value, policy, where)
        elif isinstance(cur, dict) != isinstance(value, dict):
            if policy == "error":
                raise ValueError(f"conflict at {where}")
            if policy == "override":
                out[key] = _merge({}, value, policy, where) if isinstance(value, dict) else copy.deepcopy(value)
        else:
            out[key] = copy.deepcopy(value)  # scalars and lists are replaced whole
    return out


def deep_merge(base: dict, override: dict, policy: str) -> dict:
    if policy not in ("override", "keep", "error"):
        raise ValueError(f"unknown policy: {policy!r}")
    return _merge(base, override, policy, "")
