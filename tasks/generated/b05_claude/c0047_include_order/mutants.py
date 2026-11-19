[
    ("cycle chain reported from the root instead of from the repeated file", "                chain = [f for f, _ in path[on_path[child]:]] + [child]", "                chain = [f for f, _ in path] + [child]"),
    ("includes processed in reverse order", "        includes = files[name]", "        includes = files[name][::-1]"),
    ("missing include surfaces as KeyError", "        if name not in files:\n            raise ValueError(f\"missing file: {name}\")\n", "        if name == root and name not in files:\n            raise ValueError(f\"missing file: {name}\")\n"),
]
