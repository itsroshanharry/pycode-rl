def include_order(files: dict[str, list[str]], root: str) -> list[str]:
    placed: set[str] = set()
    out: list[str] = []
    on_path: dict[str, int] = {}  # file -> its index in `path`
    path: list[list] = []  # explicit DFS stack of [file, next include index]; no recursion limit

    def push(name: str) -> None:
        if name not in files:
            raise ValueError(f"missing file: {name}")
        on_path[name] = len(path)
        path.append([name, 0])

    push(root)
    while path:
        frame = path[-1]
        name, k = frame
        includes = files[name]
        if k < len(includes):
            frame[1] += 1
            child = includes[k]
            if child in placed:
                continue
            if child in on_path:
                chain = [f for f, _ in path[on_path[child]:]] + [child]
                raise ValueError("include cycle: " + " -> ".join(chain))
            push(child)
        else:
            path.pop()
            del on_path[name]
            placed.add(name)
            out.append(name)
    return out
