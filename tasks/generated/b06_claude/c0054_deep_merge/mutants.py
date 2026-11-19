[
    ("lists concatenated instead of replaced", "            out[key] = copy.deepcopy(value)  # scalars and lists are replaced whole", "            out[key] = cur + value if isinstance(cur, list) and isinstance(value, list) else copy.deepcopy(value)"),
    ("None stored as a value instead of deleting the key", "        if value is None:\n            out.pop(key, None)\n            continue", "        if value is None:\n            out[key] = None\n            continue"),
    ("only dict-replaced-by-scalar counts as a conflict", "        elif isinstance(cur, dict) != isinstance(value, dict):", "        elif isinstance(cur, dict) and not isinstance(value, dict):"),
]
