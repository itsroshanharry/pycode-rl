```python
def build_waves(deps: dict[str, list[str]], max_parallel: int, priority: dict[str, int]) -> list[list[str]]:
    """Group build targets into parallel waves, with a limit per wave.

    `deps` maps a target to the targets it depends on (repeats in a list are
    ignored). Every name that appears as a dependency is also a target, even if
    it is not a key of `deps`. A target is READY when all its dependencies were
    built in EARLIER waves (a target finished in the current wave does not make
    others ready in that same wave).

    Repeatedly form the next wave: take all ready, unbuilt targets; if there are
    more than `max_parallel`, keep the `max_parallel` with the highest priority
    (priority[t], default 0 when missing), ties broken by name ascending. The
    others simply stay ready for later waves. List each wave's targets sorted by
    name.

    Return the list of waves. Raise ValueError if max_parallel < 1 or the
    dependencies contain a cycle (including a target depending on itself).

    >>> build_waves({"app": ["lib", "cfg"], "lib": ["base"], "cfg": []}, 2, {"cfg": 5})
    [['base', 'cfg'], ['lib'], ['app']]
    >>> build_waves({"a": [], "b": [], "c": []}, 2, {"c": 1})
    [['a', 'c'], ['b']]
    """
```
