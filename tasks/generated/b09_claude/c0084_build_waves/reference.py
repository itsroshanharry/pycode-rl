def build_waves(deps: dict[str, list[str]], max_parallel: int, priority: dict[str, int]) -> list[list[str]]:
    if max_parallel < 1:
        raise ValueError("max_parallel must be >= 1")
    graph: dict[str, set[str]] = {}
    for target, ds in deps.items():
        graph.setdefault(target, set()).update(ds)
        for d in ds:
            graph.setdefault(d, set())  # dependency-only names are targets too
    built: set[str] = set()
    waves = []
    while len(built) < len(graph):
        # "ready" uses only earlier waves: `built` is updated after the wave is chosen
        ready = [t for t in graph if t not in built and graph[t] <= built]
        if not ready:
            raise ValueError("dependency cycle")
        ready.sort(key=lambda t: (-priority.get(t, 0), t))
        wave = sorted(ready[:max_parallel])
        built.update(wave)
        waves.append(wave)
    return waves
