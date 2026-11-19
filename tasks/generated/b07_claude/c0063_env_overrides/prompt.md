```python
def env_overrides(config: dict, env: dict[str, str], prefix: str) -> dict:
    """Apply environment-variable overrides to a nested config; return a new dict.

    Only variables whose name starts with `prefix` + "__" are used (the match
    is case-SENSITIVE; e.g. prefix "APP" uses "APP__DB__PORT" but not
    "APPX__A" or "app__a"). The rest of the name is split on "__" into a key
    path, and each part is lowercased ("APP__DB__MAX_CONN" -> ["db",
    "max_conn"]; a single "_" stays inside the key). An empty part (as in
    "APP____X", "APP__A__" or "APP__") is a ValueError.

    Variables are applied in sorted order of their names. Missing
    intermediate sections are created as {}; an existing intermediate value
    that is not a dict is a ValueError, and so is overriding a value that is
    itself a dict. The new value is converted using the type of the CURRENT
    value at that path:
    - bool: "true"/"1" -> True, "false"/"0" -> False (case-insensitive),
      anything else is a ValueError;
    - int (but not bool): an optional "-" and 1+ ASCII digits, else ValueError;
    - anything else, or a missing key: the string unchanged.

    >>> env_overrides({"db": {"port": 5432, "ssl": False}}, {"APP__DB__PORT": "6543", "APP__DB__SSL": "TRUE", "APP__MODE": "dev", "OTHER": "x"}, "APP")
    {'db': {'port': 6543, 'ssl': True}, 'mode': 'dev'}
    """
```
