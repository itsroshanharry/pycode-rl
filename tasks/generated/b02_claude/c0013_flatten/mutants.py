[
    ("empty nested dicts dropped instead of kept as leaves", "        if isinstance(value, dict) and value:", "        if isinstance(value, dict):"),
    ("keys containing '.' accepted", 'any(c in k for c in ".[]")', 'any(c in k for c in "[]")'),
    ("list positions written as .i instead of [i]", 'walk(v, f"{path}[{i}]")', 'walk(v, f"{path}.{i}")'),
]
