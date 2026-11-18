```python
def matching_versions(versions: list[str], spec: str) -> list[str]:
    """Return the versions (in input order) that satisfy a range expression.

    A version is "MAJOR.MINOR.PATCH": non-negative integers without leading zeros.
    A range is one or more alternatives separated by "||" (with optional spaces
    around it); a version matches the range if it matches at least one alternative.
    An alternative is either "*" (matches everything) or one or more comparators
    separated by spaces, all of which must hold. A comparator is an operator
    (">=", "<=", ">", "<", "=") or no operator (meaning "="), immediately followed by
    a partial version with 1, 2 or 3 parts, such as "1", "1.2" or "1.2.3".
    A comparator with k parts compares only the first k parts of the version:
      "=1.2" matches 1.2.x; ">1.2" means at least 1.3.0; ">=1.2" at least 1.2.0;
      "<1.2" means below 1.2.0; "<=1.2" means anything up to 1.2.x (below 1.3.0).
    Raise ValueError if any version or the range is malformed (e.g. an empty
    alternative, an unknown operator, a space between an operator and its version,
    or leading zeros).

    >>> matching_versions(["1.2.0", "1.2.9", "1.3.0", "2.0.0"], "<=1.2 || >=2")
    ['1.2.0', '1.2.9', '2.0.0']
    >>> matching_versions(["0.9.9", "1.0.0", "1.5.1"], ">=1 <1.5")
    ['1.0.0']
    """
```
