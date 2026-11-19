```python
def resolve_import(importer: str, is_package: bool, statement: str) -> list[str]:
    """Resolve a Python `from ... import ...` statement to absolute names.

    `importer` is the dotted name of the module containing the statement;
    `is_package` says whether it is a package's __init__ (then the importer
    IS its own package) or a plain module (then its package is the importer
    minus its last component).

    `statement` is "from <source> import <names>" with single spaces around
    "from" and "import". <source> is zero or more dots followed by an optional
    dotted module name, written together (".a.b", "..", "x.y"); it must not be
    empty. <names> is "*", or a comma-separated list of items "name" or
    "name as alias" (spaces around commas and around "as" allowed),
    optionally wrapped in parentheses; a trailing comma is allowed only
    inside parentheses. All names (importer parts, module parts, imported
    names, aliases) are ASCII identifiers that are not Python keywords.

    With k leading dots (k >= 1) the base package is the importer's package
    with k - 1 trailing components removed; it is an error if the importer
    has no package, or if that would go above the top-level package. The
    source module is the base package, followed by "." and the dotted name if
    one is given. With no dots the source is the dotted name itself.

    Return "<source>.<name>" for each imported name in order (the original
    name, never the alias), or ["<source>.*"] for "*".
    Raise ValueError for a malformed input or an impossible relative import.

    >>> resolve_import("pkg.sub.mod", False, "from ..a import b, c as d")
    ['pkg.a.b', 'pkg.a.c']
    >>> resolve_import("pkg.sub", True, "from . import x")
    ['pkg.sub.x']
    """
```
