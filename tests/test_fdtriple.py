import io
import sys

from fdtriple import FdTriple


def make_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def test_defaults_are_standard_streams() -> None:
    fds = FdTriple()
    assert fds.get_in() is None
    assert fds.get_out() is None
    assert fds.get_err() is None


def test_constructor_accepts_custom_stream() -> None:
    fd_err = make_fd()
    fds = FdTriple(fd_err=fd_err)
    assert fds.get_in() is None
    assert fds.get_out() is None
    assert fds.get_err() is fd_err


def test_constructor_accepts_custom_streams() -> None:
    fd_in, fd_out, fd_err = make_fd(), make_fd(), make_fd()
    fds = FdTriple(fd_in, fd_out, fd_err)
    assert fds.get_in() is fd_in
    assert fds.get_out() is fd_out
    assert fds.get_err() is fd_err


def test_set_replaces_only_target_stream() -> None:
    fds = FdTriple()
    fd = make_fd()
    fds.set_out(fd)
    assert fds.get_out() is fd
    assert fds.get_in() is None
    assert fds.get_err() is None


def test_set_stream_is_usable_for_io() -> None:
    fds = FdTriple()
    fds.set_err(make_fd())
    fds.get_err().write("oops")
    fds.get_err().seek(0)
    assert fds.get_err().read() == "oops"
