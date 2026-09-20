import io
from collections.abc import Callable

import commands
from src.envscope import envScope
from src.fdtriple import fdTriple


def _text_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def defaultFdTriple() -> fdTriple:
    return fdTriple(_text_fd(), _text_fd(), _text_fd())


def readOut(fds: fdTriple) -> str:
    out = fds.GetOut()
    out.seek(0)
    return out.read()


def test_echo_joins_args_with_spaces() -> None:
    fds = defaultFdTriple()
    code = commands.lookup("echo")(fds, envScope(), ["echo", "hello", "big", "world"])
    assert code == 0
    assert readOut(fds) == "hello big world\n"


def test_echo_without_args_prints_empty_line() -> None:
    fds = defaultFdTriple()
    commands.lookup("echo")(fds, envScope(), ["echo"])
    assert readOut(fds) == "\n"
