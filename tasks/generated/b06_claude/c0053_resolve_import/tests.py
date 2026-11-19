import pytest
from solution import resolve_import


@pytest.mark.parametrize(
    "importer, is_package, statement, expected",
    [
        ("pkg.sub.mod", False, "from ..a import b, c as d", ["pkg.a.b", "pkg.a.c"]),
        ("pkg.sub", True, "from . import x", ["pkg.sub.x"]),
        ("pkg.sub", False, "from . import x", ["pkg.x"]),
        ("pkg.sub", True, "from ..a import b", ["pkg.a.b"]),
        ("pkg.mod", False, "from . import x", ["pkg.x"]),
        ("pkg.mod", False, "from .helpers.io import read", ["pkg.helpers.io.read"]),
        ("pkg", True, "from . import x", ["pkg.x"]),
        ("pkg", True, "from .core import *", ["pkg.core.*"]),
        ("a.b.c.d", False, "from ... import z", ["a.z"]),
        ("a.b.c.d", True, "from ... import z", ["a.b.z"]),
        ("a.b.c.d", True, "from .... import z", ["a.z"]),
        ("anything", False, "from os.path import join, split", ["os.path.join", "os.path.split"]),
        ("top", False, "from json import *", ["json.*"]),
        ("pkg.m", False, "from . import (a, b)", ["pkg.a", "pkg.b"]),
        ("pkg.m", False, "from . import (a, b,)", ["pkg.a", "pkg.b"]),
        ("pkg.m", False, "from . import (a as x,b  as  y)", ["pkg.a", "pkg.b"]),
        ("pkg.m", False, "from . import a ,b", ["pkg.a", "pkg.b"]),
        ("pkg.m", False, "from . import (x)", ["pkg.x"]),
        ("pkg.m", False, "from .a import a", ["pkg.a.a"]),
        ("p_1.Mod2", False, "from ._priv import _x", ["p_1._priv._x"]),
    ],
)
def test_examples(importer, is_package, statement, expected):
    assert list(resolve_import(importer, is_package, statement)) == expected


@pytest.mark.parametrize(
    "importer, is_package, statement",
    [
        ("mod", False, "from . import x"),
        ("mod", False, "from .a import x"),
        ("pkg", True, "from .. import x"),
        ("pkg.mod", False, "from .. import x"),
        ("pkg.sub", False, "from ..a import b"),
        ("a.b.c", True, "from .... import z"),
        ("pkg.m", False, "from  import x"),
        ("pkg.m", False, "from . import"),
        ("pkg.m", False, "from . import a,"),
        ("pkg.m", False, "from . import ()"),
        ("pkg.m", False, "from . import (*)"),
        ("pkg.m", False, "from . import a b"),
        ("pkg.m", False, "from . import a as"),
        ("pkg.m", False, "from . import 1a"),
        ("pkg.m", False, "from . import class"),
        ("pkg.m", False, "from . import a as def"),
        ("pkg.m", False, "from .class import a"),
        ("pkg.m", False, "from . a import b"),
        ("pkg.m", False, "from .a. import b"),
        ("pkg.m", False, "from .a..b import c"),
        ("pkg.m", False, "import os"),
        ("pkg.m", False, "from  .a import b"),
        ("pkg.m", False, "from .a  import b"),
        ("pkg.m", False, "from .été import b"),
        ("pkg..m", False, "from os import path"),
        ("", False, "from os import path"),
        ("pkg.m", False, "from . import (a, b"),
    ],
)
def test_invalid(importer, is_package, statement):
    with pytest.raises(ValueError):
        resolve_import(importer, is_package, statement)


def test_many_dots():
    importer = ".".join(f"p{i}" for i in range(30)) + ".leaf"
    assert list(resolve_import(importer, False, "from " + "." * 30 + " import z")) == ["p0.z"]
    with pytest.raises(ValueError):
        resolve_import(importer, False, "from " + "." * 31 + " import z")
