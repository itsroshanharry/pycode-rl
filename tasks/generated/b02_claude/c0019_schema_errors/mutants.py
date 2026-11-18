[
    ("bool accepted as int", '        return type(value) is int\n', '        return isinstance(value, int)\n'),
    ("min bound treated as exclusive", 'if "min" in schema and value < schema["min"]:', 'if "min" in schema and value <= schema["min"]:'),
    ("missing required fields reported before field errors", "        for name, sub in schema.get(\"fields\", {}).items():\n            if name in value:\n                _check(value[name], sub, f\"{path}.{name}\", errors)\n        for name in schema.get(\"required\", []):\n            if name not in value:\n                errors.append(f\"{path}.{name}: missing required field\")", "        for name in schema.get(\"required\", []):\n            if name not in value:\n                errors.append(f\"{path}.{name}: missing required field\")\n        for name, sub in schema.get(\"fields\", {}).items():\n            if name in value:\n                _check(value[name], sub, f\"{path}.{name}\", errors)"),
]
