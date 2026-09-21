import io
import sys

from fdtriple import fdTriple


def make_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def test_defaults_are_standard_streams() -> None:
    fds = fdTriple()
    assert fds.GetIn() is None
    assert fds.GetOut() is None
    assert fds.GetErr() is None


def test_constructor_accepts_custom_stream() -> None:
    fd_err = make_fd()
    fds = fdTriple(fd_err=fd_err)
    assert fds.GetIn() is None
    assert fds.GetOut() is None
    assert fds.GetErr() is fd_err


def test_constructor_accepts_custom_streams() -> None:
    fd_in, fd_out, fd_err = make_fd(), make_fd(), make_fd()
    fds = fdTriple(fd_in, fd_out, fd_err)
    assert fds.GetIn() is fd_in
    assert fds.GetOut() is fd_out
    assert fds.GetErr() is fd_err


def test_set_replaces_only_target_stream() -> None:
    fds = fdTriple()
    fd = make_fd()
    fds.SetOut(fd)
    assert fds.GetOut() is fd
    assert fds.GetIn() is None
    assert fds.GetErr() is None


def test_set_stream_is_usable_for_io() -> None:
    fds = fdTriple()
    fds.SetErr(make_fd())
    fds.GetErr().write("oops")
    fds.GetErr().seek(0)
    assert fds.GetErr().read() == "oops"
