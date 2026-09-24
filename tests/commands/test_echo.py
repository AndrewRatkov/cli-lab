import io
from collections.abc import Callable

import commands
from runtime import EnvScope, FdTriple


def _text_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def default_fd_triple() -> FdTriple:
    return FdTriple(_text_fd(), _text_fd(), _text_fd())


def read_out(fds: FdTriple) -> str:
    out = fds.get_out()
    out.seek(0)
    return out.read()


def test_echo_joins_args_with_spaces() -> None:
    fds = default_fd_triple()
    code = commands.lookup("echo")(fds, EnvScope(), ["echo", "hello", "big", "world"])
    assert code == 0
    assert read_out(fds) == "hello big world\n"


def test_echo_without_args_prints_empty_line() -> None:
    fds = default_fd_triple()
    commands.lookup("echo")(fds, EnvScope(), ["echo"])
    assert read_out(fds) == "\n"
