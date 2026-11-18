def _type_ok(value, t: str) -> bool:
    if t == "int":
        return type(value) is int
    if t == "float":
        return type(value) in (int, float)
    if t == "str":
        return type(value) is str
    if t == "bool":
        return type(value) is bool
    if t == "null":
        return value is None
    if t == "list":
        return type(value) is list
    if t == "dict":
        return type(value) is dict
    raise ValueError(f"unknown schema type {t!r}")


def _check(value, schema: dict, path: str, errors: list[str]) -> None:
    t = schema["type"]
    if not _type_ok(value, t):
        errors.append(f"{path}: expected {t}")
        return
    if t in ("int", "float"):
        if "min" in schema and value < schema["min"]:
            errors.append(f"{path}: below min {schema['min']}")
        if "max" in schema and value > schema["max"]:
            errors.append(f"{path}: above max {schema['max']}")
    elif t == "str":
        if "max_len" in schema and len(value) > schema["max_len"]:
            errors.append(f"{path}: longer than {schema['max_len']}")
    elif t == "list" and "items" in schema:
        for i, item in enumerate(value):
            _check(item, schema["items"], f"{path}[{i}]", errors)
    elif t == "dict":
        for name, sub in schema.get("fields", {}).items():
            if name in value:
                _check(value[name], sub, f"{path}.{name}", errors)
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{path}.{name}: missing required field")


def schema_errors(value, schema: dict) -> list[str]:
    errors: list[str] = []
    _check(value, schema, "$", errors)
    return errors
