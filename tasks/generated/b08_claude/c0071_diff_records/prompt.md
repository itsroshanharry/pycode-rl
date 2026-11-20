```python
def diff_records(old: dict, new: dict) -> dict[str, list[str]]:
    """Diff two flat records (string keys; JSON-like values: None, bool, int,
    float, str, and lists/dicts of those, nested to any depth).

    Return {"added": [...], "removed": [...], "changed": [...]}:
    - added: keys in `new` but not in `old`;
    - removed: keys in `old` but not in `new`;
    - changed: keys in both whose values are NOT strictly equal.
    Each list is sorted (plain string order).

    Strict equality: the two values must have exactly the same type and be
    equal, and lists/dicts are compared element by element with the same
    strict rule at every depth. So 1, 1.0 and True are all different from
    each other, and so are [1] and [True]. Dicts are equal when they have the
    same keys and strictly equal values (key order does not matter).

    >>> diff_records({"a": 1, "b": 2, "c": [1, 2]}, {"b": 2.0, "c": [1, 2], "d": None})
    {'added': ['d'], 'removed': ['a'], 'changed': ['b']}
    """
```
