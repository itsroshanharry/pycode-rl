```python
def include_order(files: dict[str, list[str]], root: str) -> list[str]:
    """Order config files so that every file comes after all the files it includes.

    `files` maps each file name to the names it includes, in order. Start at
    `root` and process files depth-first: to process a file, process each of
    its includes in the listed order (skipping any file that has already been
    placed), then place the file itself. Return the placed files in placement
    order; only files reachable from `root` appear, and `root` is last.

    Raise ValueError("missing file: <name>") when a file that must be processed
    (including `root`) is not a key of `files`.
    Raise ValueError("include cycle: <chain>") when processing reaches a file
    that is still being processed. The chain lists the include path from the
    earlier occurrence of that file down to the file that includes it again,
    then repeats it, joined by " -> " (for example "b -> c -> b"; a file that
    includes itself gives "a -> a").

    Include chains can be thousands of files deep.

    >>> include_order({"app": ["db", "log"], "db": ["log"], "log": []}, "app")
    ['log', 'db', 'app']
    """
```
