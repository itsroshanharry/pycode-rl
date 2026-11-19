import pytest
from solution import env_overrides

BASE = {"db": {"port": 5432, "ssl": False, "host": "localhost", "pool": {"max_conn": 10}}, "debug": False, "name": "svc", "ratio": 1.5}


@pytest.mark.parametrize(
    "config, env, prefix, expected",
    [
        ({"db": {"port": 5432, "ssl": False}}, {"APP__DB__PORT": "6543", "APP__DB__SSL": "TRUE", "APP__MODE": "dev", "OTHER": "x"}, "APP",
         {"db": {"port": 6543, "ssl": True}, "mode": "dev"}),
        ({}, {}, "APP", {}),
        (BASE, {}, "APP", BASE),
        (BASE, {"APP__DB__POOL__MAX_CONN": "-3"}, "APP", {**BASE, "db": {**BASE["db"], "pool": {"max_conn": -3}}}),
        (BASE, {"APP__DEBUG": "1"}, "APP", {**BASE, "debug": True}),
        (BASE, {"APP__DEBUG": "0"}, "APP", {**BASE, "debug": False}),
        (BASE, {"APP__DEBUG": "False"}, "APP", {**BASE, "debug": False}),
        (BASE, {"APP__NAME": "  spaced  "}, "APP", {**BASE, "name": "  spaced  "}),
        (BASE, {"APP__RATIO": "2.5"}, "APP", {**BASE, "ratio": "2.5"}),
        (BASE, {"APP__DB__PORT": "007"}, "APP", {**BASE, "db": {**BASE["db"], "port": 7}}),
        (BASE, {"APPX__NAME": "no", "app__name": "no", "APP_NAME": "no", "XAPP__NAME": "no"}, "APP", BASE),
        ({}, {"APP__A__B__C": "x"}, "APP", {"a": {"b": {"c": "x"}}}),
        ({"a": {}}, {"APP__A__NEW": "1"}, "APP", {"a": {"new": "1"}}),
        ({"a": 1}, {"APP__A": "2", "APP__B": "3"}, "APP", {"a": 2, "b": "3"}),
        ({"x": None}, {"APP__X": "v"}, "APP", {"x": "v"}),
        ({"k": True}, {"P__K": "tRuE"}, "P", {"k": True}),
        ({"k": 0}, {"P__K": "1"}, "P", {"k": 1}),
        ({}, {"MY_APP__A_B": "z"}, "MY_APP", {"a_b": "z"}),
        ({"a": "x"}, {"APP__A": "1", "APP__a": "2"}, "APP", {"a": "2"}),
        ({"db": {}}, {"APP__DB___PORT": "1"}, "APP", {"db": {"_port": "1"}}),
    ],
)
def test_examples(config, env, prefix, expected):
    assert env_overrides(config, env, prefix) == expected


@pytest.mark.parametrize(
    "config, env",
    [
        (BASE, {"APP__DEBUG": "yes"}),
        (BASE, {"APP__DEBUG": ""}),
        (BASE, {"APP__DB__PORT": "54x"}),
        (BASE, {"APP__DB__PORT": "+5"}),
        (BASE, {"APP__DB__PORT": " 5"}),
        (BASE, {"APP__DB__PORT": "５"}),
        (BASE, {"APP__DB": "flat"}),
        (BASE, {"APP__NAME__X": "1"}),
        (BASE, {"APP____X": "1"}),
        (BASE, {"APP__DB__": "1"}),
        (BASE, {"APP__": "1"}),
        ({}, {"APP__A": "1", "APP__A__B": "2"}),
    ],
)
def test_invalid(config, env):
    with pytest.raises(ValueError):
        env_overrides(config, env, "APP")
