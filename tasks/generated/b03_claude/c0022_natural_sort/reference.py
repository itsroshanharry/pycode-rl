import re

_RUN = re.compile(r"[0-9]+|[^0-9]+")


def _key(name: str):
    runs = []
    for run in _RUN.findall(name):
        if run[0] in "0123456789":
            runs.append((0, int(run), ""))
        else:
            runs.append((1, 0, run.casefold()))
    return (runs, name)


def natural_sort(names: list[str]) -> list[str]:
    return sorted(names, key=_key)  # sorted() is stable for exact duplicates
