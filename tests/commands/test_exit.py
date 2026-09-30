import io

import pytest

import commands
from commands import ShellExit
from runtime import EnvScope, FdTriple


def _text_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def default_fd_triple() -> FdTriple:
    return FdTriple(_text_fd(), _text_fd(), _text_fd())


def run_exit(*args: str) -> None:
    commands.lookup("exit")(default_fd_triple(), EnvScope(), ["exit", *args])


def test_exit_without_code() -> None:
    with pytest.raises(ShellExit) as e:
        run_exit()
    assert e.value.code == 0


def test_exit_with_code() -> None:
    with pytest.raises(ShellExit) as e:
        run_exit("3")
    assert e.value.code == 3


def test_exit_with_bad_code() -> None:
    with pytest.raises(ShellExit) as e:
        run_exit("abc")
    assert e.value.code == 2
