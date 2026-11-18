def _check_key(k) -> None:
    if type(k) is not str or not k or any(c in k for c in ".[]"):
        raise ValueError(f"invalid key: {k!r}")


def flatten(obj: dict) -> dict:
    if not isinstance(obj, dict):
        raise TypeError("flatten() expects a dict")
    out: dict = {}

    def walk(value, path: str) -> None:
        if isinstance(value, dict) and value:
            for k, v in value.items():
                _check_key(k)
                walk(v, f"{path}.{k}")
        elif isinstance(value, list) and value:
            for i, v in enumerate(value):
                walk(v, f"{path}[{i}]")
        else:
            out[path] = value

    for k, v in obj.items():
        _check_key(k)
        walk(v, k)
    return out
