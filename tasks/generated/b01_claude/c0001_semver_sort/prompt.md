```python
def semver_sort(versions: list[str]) -> list[str]:
    """Sort version strings by Semantic Versioning precedence, lowest first.

    A version is MAJOR.MINOR.PATCH, optionally followed by "-" and a pre-release
    (dot-separated identifiers), then optionally "+" and build metadata
    (dot-separated identifiers). MAJOR, MINOR and PATCH are non-negative decimal
    integers without leading zeros. Every identifier is non-empty and uses only
    ASCII letters, digits and "-". A pre-release identifier made only of digits
    must not have a leading zero (build metadata may). Raise ValueError if any
    string is not a valid version.

    Precedence: compare MAJOR, MINOR, PATCH numerically. A version with a
    pre-release is lower than the same MAJOR.MINOR.PATCH without one. Two
    pre-releases are compared identifier by identifier from the left: digit-only
    identifiers numerically, other identifiers in ASCII order, and a digit-only
    identifier is always lower than any other identifier. If all shared
    identifiers are equal, the pre-release with fewer identifiers is lower.
    Build metadata is ignored. Versions of equal precedence keep their input order.

    >>> semver_sort(["1.0.0", "1.0.0-alpha", "0.9.12"])
    ['0.9.12', '1.0.0-alpha', '1.0.0']
    >>> semver_sort(["1.0.0-alpha.beta", "1.0.0-alpha.1", "1.0.0-alpha"])
    ['1.0.0-alpha', '1.0.0-alpha.1', '1.0.0-alpha.beta']
    """
```
