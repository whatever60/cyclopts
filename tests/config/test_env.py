from dataclasses import dataclass

import pytest

from cyclopts.argument import ArgumentCollection
from cyclopts.config import Env
from cyclopts.token import Token


@pytest.fixture
def apps():
    """App is only used as a dictionary in these tests."""
    return [{"function1": None}]


def test_config_env_default(apps, monkeypatch):
    def foo(bar: int):
        pass

    argument_collection = ArgumentCollection._from_callable(foo)

    monkeypatch.setenv("CYCLOPTS_TEST_APP_BAR", "100")
    monkeypatch.setenv("CYCLOPTS_TEST_APP_SOMETHING_ELSE", "100")
    Env("CYCLOPTS_TEST_APP_", command=False)(apps, (), argument_collection)

    assert len(argument_collection[0].tokens) == 1
    assert argument_collection[0].tokens[0].keyword == "CYCLOPTS_TEST_APP_BAR"
    assert argument_collection[0].tokens[0].value == "100"
    assert argument_collection[0].tokens[0].source == "env"
    assert argument_collection[0].tokens[0].index == 0
    assert argument_collection[0].tokens[0].keys == ()


def test_config_env_default_already_populated(apps, monkeypatch):
    def foo(bar: int):
        pass

    argument_collection = ArgumentCollection._from_callable(foo)
    argument_collection[0].append(Token(keyword="--bar", value="500", source="cli"))

    monkeypatch.setenv("CYCLOPTS_TEST_APP_BAR", "100")
    monkeypatch.setenv("CYCLOPTS_TEST_APP_SOMETHING_ELSE", "100")
    Env("CYCLOPTS_TEST_APP_", command=False)(apps, (), argument_collection)

    assert len(argument_collection[0].tokens) == 1
    assert argument_collection[0].tokens[0].keyword == "--bar"
    assert argument_collection[0].tokens[0].value == "500"
    assert argument_collection[0].tokens[0].source == "cli"
    assert argument_collection[0].tokens[0].index == 0
    assert argument_collection[0].tokens[0].keys == ()


def test_config_env_command_true(apps, monkeypatch):
    def foo(bar: int):
        pass

    argument_collection = ArgumentCollection._from_callable(foo)

    monkeypatch.setenv("CYCLOPTS_TEST_APP_FOO_BAR", "100")
    Env("CYCLOPTS_TEST_APP_", command=True)(apps, ("foo",), argument_collection)

    assert len(argument_collection[0].tokens) == 1
    assert argument_collection[0].tokens[0].keyword == "CYCLOPTS_TEST_APP_FOO_BAR"
    assert argument_collection[0].tokens[0].value == "100"
    assert argument_collection[0].tokens[0].source == "env"
    assert argument_collection[0].tokens[0].index == 0
    assert argument_collection[0].tokens[0].keys == ()


def test_config_env_dict(apps, monkeypatch):
    def foo(bar_bar: dict):
        pass

    ac = ArgumentCollection._from_callable(foo)

    monkeypatch.setenv("CYCLOPTS_TEST_APP_BAR_BAR_BUZZ", "100")
    monkeypatch.setenv("CYCLOPTS_TEST_APP_BAR_BAR_FIZZ", "200")

    Env("CYCLOPTS_TEST_APP_", command=False)(apps, (), ac)

    assert len(ac[0].tokens) == 2

    assert ac[0].tokens[0].keyword == "CYCLOPTS_TEST_APP_BAR_BAR_BUZZ"
    assert ac[0].tokens[0].value == "100"
    assert ac[0].tokens[0].source == "env"
    assert ac[0].tokens[0].index == 0
    assert ac[0].tokens[0].keys == ("buzz",)

    assert ac[0].tokens[1].keyword == "CYCLOPTS_TEST_APP_BAR_BAR_FIZZ"
    assert ac[0].tokens[1].value == "200"
    assert ac[0].tokens[1].source == "env"
    assert ac[0].tokens[1].index == 0
    assert ac[0].tokens[1].keys == ("fizz",)


def test_config_env_dataclass(apps, monkeypatch):
    @dataclass
    class User:
        fizz_fizz: int
        buzz_buzz: int

    def foo(bar_bar: User):
        pass

    ac = ArgumentCollection._from_callable(foo)

    monkeypatch.setenv("CYCLOPTS_TEST_APP_BAR_BAR_BUZZ_BUZZ", "100")
    monkeypatch.setenv("CYCLOPTS_TEST_APP_BAR_BAR_FIZZ_FIZZ", "200")

    Env("CYCLOPTS_TEST_APP_", command=False)(apps, (), ac)

    assert len(ac) == 3
    assert len(ac[1].tokens) == 1
    assert len(ac[2].tokens) == 1

    assert ac[1].tokens[0].keyword == "CYCLOPTS_TEST_APP_BAR_BAR_FIZZ_FIZZ"
    assert ac[1].tokens[0].value == "200"
    assert ac[1].tokens[0].source == "env"
    assert ac[1].tokens[0].index == 0
    assert ac[1].tokens[0].keys == ()

    assert ac[2].tokens[0].keyword == "CYCLOPTS_TEST_APP_BAR_BAR_BUZZ_BUZZ"
    assert ac[2].tokens[0].value == "100"
    assert ac[2].tokens[0].source == "env"
    assert ac[2].tokens[0].index == 0
    assert ac[2].tokens[0].keys == ()


def test_config_env_kwargs(app, assert_parse_args, monkeypatch):
    @app.default
    def default(a: str, **kwargs):
        pass

    monkeypatch.setenv("CYCLOPTS_TEST_APP_TWO_WORDS", "test value")
    app.config = Env("CYCLOPTS_TEST_APP_")

    assert_parse_args(default, "a_value", a="a_value", two_words="test value")
