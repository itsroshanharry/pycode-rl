```python
def deep_merge(base: dict, override: dict, policy: str) -> dict:
    """Deep-merge two JSON-like dicts (string keys; values are dicts, lists,
    strings, numbers, booleans or None) and return a new dict.

    For each key of `override`, in order:
    - value None: DELETE the key from the result (no-op if it is absent).
    - key absent from the result: add it. If the value is a dict, it is
      merged into an empty dict, so None values inside it delete nothing and
      are simply dropped, at every depth.
    - both values are dicts: merge them recursively with the same rules.
    - exactly one of the two is a dict (a conflict): follow `policy`:
      "override" takes the override value (cleaned of None as above),
      "keep" keeps the base value, "error" raises
      ValueError("conflict at <path>") where <path> is the keys from the top
      joined by "." (e.g. "conflict at db.port").
    - otherwise (neither is a dict): the override value replaces the base
      value. Lists are replaced whole, never merged or concatenated, and
      their contents are taken as they are (a None inside a list stays).
    None values already in `base` are ordinary values.
    Keys keep their order: base keys first (in base order), then new keys in
    override order. Raise ValueError for an unknown policy.

    >>> deep_merge({"db": {"host": "a", "port": 1}, "tags": [1]}, {"db": {"port": None}, "tags": [2]}, "error")
    {'db': {'host': 'a'}, 'tags': [2]}
    """
```
