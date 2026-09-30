import io
import os

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


def test_pwd_prints_cwd() -> None:
    fds = default_fd_triple()
    assert commands.lookup("pwd")(fds, EnvScope(), ["pwd"]) == 0
    assert read_out(fds) == os.getcwd() + "\n"
