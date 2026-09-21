import io
from pathlib import Path

from main import run
from fdtriple import FdTriple


def make_fd() -> io.TextIOWrapper:
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def test1() -> None:
    string: str = "echo hello"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test2(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("Hello, world!\n")

    string: str = "cat " + str(f)
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "Hello, world!\n"


def test3() -> None:
    string: str = "echo hello | cat"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\n"


def test4() -> None:
    string: str = "echo hello; echo world"
    fds = FdTriple()
    res_fd = make_fd()
    fds.set_out(res_fd)

    run(string, fds)
    res_fd.seek(0)
    assert res_fd.read() == "hello\nworld\n"
